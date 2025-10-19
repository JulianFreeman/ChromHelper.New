import requests
from PySide6.QtCore import QObject, Signal
from app.common.utils import APIException, SAFE_MARKS_API


# --- API 工作线程 ---
class ApiWorker(QObject):
    """在单独的线程中执行网络请求，避免 GUI 冻结"""
    # 定义信号
    queryNecessaryFinished = Signal(list)
    addBatchFinished = Signal(dict)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.session = requests.Session()

    @staticmethod
    def _handle_response(response):
        """辅助函数：检查 HTTP 响应"""
        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
                raise APIException(f"API 错误 (状态 {response.status_code}): {detail}")
            except requests.JSONDecodeError:
                raise APIException(f"API 错误 (状态 {response.status_code}): {response.text}")
        return response.json()

    def do_query_necessary(self):
        """执行 query_necessary 操作"""
        try:
            response = self.session.get(f"{SAFE_MARKS_API}/query_necessary")
            data = self._handle_response(response)
            self.queryNecessaryFinished.emit(data)
        except Exception as e:
            self.error.emit(str(e))

    def do_add_batch(self, extensions: list[dict[str, str | int]]):
        """执行 add_batch 操作"""
        try:
            response = self.session.post(f"{SAFE_MARKS_API}/add_batch", json=extensions)
            data = self._handle_response(response)
            self.addBatchFinished.emit(data)
        except Exception as e:
            self.error.emit(str(e))
