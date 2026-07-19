import subprocess
import sys
import tempfile
import os


class CodeExecutor:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def run(self, code: str) -> dict:
        """执行代码并返回结果"""
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as f:
                f.write(code)
                temp_path = f.name
            
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env
            )
            
            os.unlink(temp_path)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "执行超时"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }
    
    async def run_test(self, code: str, test_code: str) -> dict:
        """运行测试"""
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as f:
                f.write(f"{code}\n\n{test_code}")
                temp_path = f.name
            
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            
            result = subprocess.run(
                [sys.executable, "-m", "pytest", temp_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env
            )
            
            os.unlink(temp_path)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "测试执行超时"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }
