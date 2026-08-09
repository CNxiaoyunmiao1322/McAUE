import os
import glob
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from .task import DownloadTask
from .verify import sha256_file


DEFAULT_HEADERS = {
    "User-Agent": "Downloader/1.0 (multi-thread)"
}


class DownloadEngine:
    MAX_THREADS = 512

    def __init__(self, threads=32, retry=3, cdn=None, headers=None, verify=True):
        self.threads = min(max(1, threads), self.MAX_THREADS)
        self.retry = max(0, retry)
        self.cdn = cdn or []
        self.headers = {**DEFAULT_HEADERS, **(headers or {})}
        self.verify = verify

        self.tasks = []
        self.callback = None

        self.paused = threading.Event()
        self.cancelled = threading.Event()

        self.lock = threading.Lock()
        self.total = 0
        self.done = 0
        self.start_time = 0
        self._last_done = 0
        self._last_time = 0
        self.phase = "idle"


    def set_callback(self, callback):
        self.callback = callback


    def add_task(self, url, save, sha256=None):
        self.tasks.append(
            DownloadTask(url, save, sha256)
        )


    def pause(self):
        self.paused.set()


    def resume(self):
        if self.cancelled.is_set():
            return
        self.paused.clear()


    def cancel(self):
        self.cancelled.set()
        self.paused.clear()


    def _download(self, task):
        self.phase = "downloading"
        counted = False
        for retry in range(self.retry + 1):
            try:
                size = self._get_size(task.url)
                if not counted:
                    with self.lock:
                        self.total += size
                    counted = True
                self._download_file(task, size)
                if self.cancelled.is_set():
                    return
                if task.sha256 and self.verify:
                    if sha256_file(task.save).lower() != task.sha256.lower():
                        self._cleanup_parts(task)
                        if os.path.exists(task.save):
                            os.remove(task.save)
                        raise Exception("SHA256 mismatch")
                return
            except Exception:
                if retry >= self.retry:
                    raise


    def _cleanup_parts(self, task):
        for part in glob.glob(f"{task.save}.part*"):
            try:
                os.remove(part)
            except OSError:
                pass


    def _get_size(self, url):
        try:
            r = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            r.raise_for_status()
            size = int(r.headers.get("Content-Length", 0))
            if size > 0:
                return size
        except Exception:
            pass

        with requests.get(url, headers=self.headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            return int(r.headers.get("Content-Length", 0))


    def _split_parts(self, size):
        if size <= 0:
            raise Exception("Cannot determine file size")

        threads = min(self.threads, max(1, size))
        block = size // threads
        parts = []
        for i in range(threads):
            start = i * block
            end = size - 1 if i == threads - 1 else start + block - 1
            parts.append((start, end, i))
        return parts


    def _download_file(self, task, size):
        url = task.url

        if size <= 0:
            self._download_stream(task, url)
            return

        parts = self._split_parts(size)

        def worker(item):
            start, end, idx = item
            part = f"{task.save}.part{idx}"

            resume_from = 0
            if os.path.exists(part):
                resume_from = os.path.getsize(part)
                if resume_from > (end - start + 1):
                    os.remove(part)
                    with self.lock:
                        self.done -= resume_from
                    resume_from = 0

            current = start + resume_from
            if current > end:
                return

            headers = {**self.headers, "Range": f"bytes={current}-{end}"}

            local_done = 0
            FLUSH_THRESHOLD = 4 * 1024 * 1024

            def flush():
                nonlocal local_done
                if local_done > 0:
                    with self.lock:
                        self.done += local_done
                    local_done = 0

            with requests.get(url, headers=headers, stream=True, timeout=30) as res:
                if res.status_code == 200:
                    if len(parts) > 1:
                        raise Exception(
                            "Server does not support range requests; "
                            "cannot download with multiple threads"
                        )
                    mode = "wb"
                elif res.status_code == 206:
                    mode = "ab"
                else:
                    res.raise_for_status()

                with open(part, mode) as f:
                    for chunk in res.iter_content(1024 * 1024):
                        if self.cancelled.is_set():
                            flush()
                            return
                        while self.paused.is_set() and not self.cancelled.is_set():
                            time.sleep(0.2)
                        if chunk:
                            f.write(chunk)
                            local_done += len(chunk)
                            if local_done >= FLUSH_THRESHOLD:
                                flush()
            flush()

        with ThreadPoolExecutor(max_workers=len(parts)) as pool:
            list(pool.map(worker, parts))

        if self.cancelled.is_set():
            return

        self.phase = "merging"

        with open(task.save, "wb") as out:
            for i, (start, end, idx) in enumerate(parts):
                part = f"{task.save}.part{i}"
                expected = end - start + 1
                if not os.path.exists(part):
                    raise Exception(f"Missing part file: {part}")
                if os.path.getsize(part) != expected:
                    raise Exception(
                        f"Part {i} incomplete: expected {expected} bytes, "
                        f"got {os.path.getsize(part)}"
                    )
                with open(part, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        out.write(chunk)
                os.remove(part)


    def _download_stream(self, task, url):
        local_done = 0
        FLUSH_THRESHOLD = 4 * 1024 * 1024

        with requests.get(url, headers=self.headers, stream=True, timeout=30) as res:
            res.raise_for_status()
            with open(task.save, "wb") as f:
                for chunk in res.iter_content(1024 * 1024):
                    if self.cancelled.is_set():
                        break
                    while self.paused.is_set() and not self.cancelled.is_set():
                        time.sleep(0.2)
                    if chunk:
                        f.write(chunk)
                        local_done += len(chunk)
                        if local_done >= FLUSH_THRESHOLD:
                            with self.lock:
                                self.done += local_done
                            local_done = 0

        if local_done > 0:
            with self.lock:
                self.done += local_done


    def _report(self):
        while not self.cancelled.is_set():
            time.sleep(1)
            now = time.time()
            with self.lock:
                downloaded = self.done
                elapsed = now - self.start_time
                last = self._last_time
                last_done = self._last_done
                if last > 0 and now > last:
                    speed = (downloaded - last_done) / (now - last)
                else:
                    speed = downloaded / max(elapsed, 1)
                self._last_time = now
                self._last_done = downloaded
                total = self.total

            percent = downloaded / total * 100 if total > 0 else 0

            if self.callback:
                self.callback({
                    "downloaded": downloaded,
                    "total": total,
                    "speed": speed,
                    "elapsed": elapsed,
                    "phase": self.phase,
                    "percent": percent
                })


    def start(self):
        self.cancelled.clear()
        self.paused.clear()
        self.phase = "downloading"

        self.start_time = time.time()
        self.total = 0
        self.done = 0

        for task in self.tasks:
            for part in glob.glob(f"{task.save}.part*"):
                if os.path.exists(part):
                    self.done += os.path.getsize(part)

        self._last_time = self.start_time
        self._last_done = self.done

        reporter = threading.Thread(
            target=self._report,
            daemon=True
        )
        reporter.start()

        try:
            for task in self.tasks:
                if self.cancelled.is_set():
                    break
                self._download(task)
        finally:
            self.phase = "done"
            self.cancelled.set()
