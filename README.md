# LeetCoder

<div align="center">

自動化 LeetCode 解題記錄系統，一鍵生成結構清晰的解題文件。

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 目錄

- [功能特色](#功能特色)
- [系統需求](#系統需求)
- [安裝](#安裝)
- [快速開始](#快速開始)
- [生成的文件格式](#生成的文件格式)
- [項目結構](#項目結構)
- [使用工作流程](#使用工作流程)
- [常用數據結構](#常用數據結構)
- [命令參考](#命令參考)
- [技術細節](#技術細節)
- [常見問題](#常見問題)
- [開發者指南](#開發者指南)
- [開發計劃](#開發計劃)
- [貢獻](#貢獻)
- [License](#license)

## 功能特色

✨ **全自動化** - 從 LeetCode 獲取題目資訊，自動生成 Python 解題文件
📁 **結構清晰** - 每題獨立文件，包含完整題目描述、範例和標籤
🔄 **版本追蹤** - 支持同一題目多個解法版本
🔍 **便捷管理** - 搜索、統計、列表等功能一應俱全
🎨 **美觀輸出** - Rich library 提供彩色終端輸出

## 快速預覽

一條命令即可生成完整的題目文件：

```bash
$ uv run python main.py add 1
✅ Created: p0001_two_sum.py
✓ Added: 1. Two Sum (Easy)
```

生成的文件包含：
- ✅ 完整的題目描述和範例
- ✅ 函數簽名框架
- ✅ 測試代碼區塊
- ✅ 題目標籤和難度
- ✅ LeetCode 鏈接

查看統計：

```bash
$ uv run python main.py stats
╭─────────────────────────────── Total Problems ───────────────────────────────╮
│ 4                                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
    By Difficulty
  Easy             2
  Medium           2
```

## 系統需求

- Python 3.11+
- uv (推薦) 或 pip

## 安裝

### 使用 uv (推薦)

```bash
# 1. 安裝依賴
uv sync

# 2. 開始使用
uv run python main.py add 1
```

### 使用 pip

```bash
# 1. 安裝依賴
pip install -e .

# 2. 開始使用
python main.py add 1
```

## 快速開始

### 添加題目

```bash
# 通過題號添加
uv run python main.py add 1

# 通過題目 slug 添加
uv run python main.py add two-sum

# 批量添加多個題目
uv run python main.py add 1 2 15 20
```

### 查看所有題目

```bash
uv run python main.py list
```

輸出示例：
```
                                  All Problems
┌────┬─────────────────┬────────────┬────────────────────┬─────────────────────┐
│ ID │ Title           │ Difficulty │ Tags               │ File                │
├────┼─────────────────┼────────────┼────────────────────┼─────────────────────┤
│  1 │ Two Sum         │    Easy    │ Array, Hash Table  │ p0001_two_sum.py    │
│  2 │ Add Two Numbers │   Medium   │ Linked List, Math, │ p0002_add_two_numb… │
│ 15 │ 3Sum            │   Medium   │ Array, Two         │ p0015_3sum.py       │
│    │                 │            │ Pointers, Sorting  │                     │
└────┴─────────────────┴────────────┴────────────────────┴─────────────────────┘

Total: 3 problem(s)
```

### 搜索題目

```bash
# 按標題關鍵字搜索
uv run python main.py search "two"

# 按標籤搜索
uv run python main.py search -t Array
```

### 查看統計

```bash
uv run python main.py stats
```

輸出示例：
```
╭─────────────────────────────── Total Problems ───────────────────────────────╮
│ 3                                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

    By Difficulty
  Difficulty   Count
  Easy             1
  Medium           2

      Top 10 Tags
  Tag            Count
  Array              2
  Hash Table         1
  Linked List        1
```

## 生成的文件格式

添加題目後，會在 `LeetCodeSolutions/` 目錄生成對應的文件：

```python
"""
LeetCode 1. Two Sum

Difficulty: Easy
Tags: Array, Hash Table

Given an array of integers nums and an integer target, return
indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution,
and you may not use the same element twice.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9

Link: https://leetcode.com/problems/two-sum/
"""

# from typing import List


class Solution:
    """Solution for Two Sum."""

    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """
        TODO: Add solution description

        Args:
            TODO: Describe parameters

        Returns:
            TODO: Describe return value

        Time Complexity: O(?)
        Space Complexity: O(?)
        """
        pass


if __name__ == "__main__":
    # Test cases
    sol = Solution()

    # TODO: Add test cases
    # Example:
    # result = sol.twoSum([2, 7, 11, 15], 9)
    # assert result == [0, 1]
    # print("✅ All test cases passed!")

    print("⚠️  Add your test cases above")
```

## 項目結構

```
leetcoder/
├── main.py                          # CLI 入口
├── src/
│   ├── __init__.py
│   ├── leetcode_api.py             # LeetCode GraphQL API 客戶端
│   ├── solution_generator.py       # 解題文件生成器
│   └── problem_index.py            # 題目索引管理
├── LeetCodeSolutions/              # 解題目錄
│   ├── __init__.py
│   ├── p0001_two_sum.py           # 題目文件
│   ├── p0002_add_two_numbers.py
│   ├── p0015_3sum.py
│   └── utils/                      # 通用數據結構
│       ├── __init__.py
│       ├── list_node.py           # 鏈表節點定義
│       └── tree_node.py           # 二叉樹節點定義
├── data/
│   └── problems.json               # 題目索引（自動生成）
├── pyproject.toml                  # 項目配置
└── README.md                       # 使用文檔
```

## 使用工作流程

### 1️⃣ 添加題目
使用 `add` 命令生成題目文件框架：
```bash
uv run python main.py add 1
```

### 2️⃣ 編寫代碼
在生成的文件中實現解法：
```python
def twoSum(self, nums: List[int], target: int) -> List[int]:
    """Hash Map 解法"""
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### 3️⃣ 添加筆記
填寫解題思路、時間空間複雜度：
```python
def twoSum(self, nums: List[int], target: int) -> List[int]:
    """
    使用 Hash Map 優化查找

    思路：
    1. 遍歷數組，對於每個數字 num
    2. 檢查 target - num 是否已經在字典中
    3. 如果在，返回兩個索引
    4. 如果不在，將當前數字加入字典

    Time Complexity: O(n) - 單次遍歷
    Space Complexity: O(n) - 字典存儲
    """
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### 4️⃣ 測試運行
添加測試案例並運行文件：
```python
if __name__ == "__main__":
    sol = Solution()

    # 測試案例 1
    result = sol.twoSum([2, 7, 11, 15], 9)
    assert result == [0, 1], f"Expected [0, 1], got {result}"

    # 測試案例 2
    result = sol.twoSum([3, 2, 4], 6)
    assert result == [1, 2], f"Expected [1, 2], got {result}"

    print("✅ All test cases passed!")
```

運行：
```bash
uv run python LeetCodeSolutions/p0001_two_sum.py
```

### 5️⃣ 版本迭代
如需優化，添加新的解法版本：
```python
class Solution:
    def twoSum_v1(self, nums: List[int], target: int) -> List[int]:
        """
        暴力解法 - 第一次提交
        Time: O(n²), Space: O(1)
        """
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []

    def twoSum_v2(self, nums: List[int], target: int) -> List[int]:
        """
        Hash Map 優化 - 第二次提交
        Time: O(n), Space: O(n)
        """
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
```

## 常用數據結構

項目提供了 LeetCode 常用的數據結構，開箱即用：

### 鏈表 (ListNode)

```python
from LeetCodeSolutions.utils import ListNode

# 從列表創建鏈表
head = ListNode.from_list([1, 2, 3, 4])
print(head)  # 輸出: 1 -> 2 -> 3 -> 4

# 鏈表轉列表
values = head.to_list()  # [1, 2, 3, 4]

# 手動創建
head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
```

### 二叉樹 (TreeNode)

```python
from LeetCodeSolutions.utils import TreeNode

# 從列表創建二叉樹（層序遍歷）
root = TreeNode.from_list([1, 2, 3, None, 4])
"""
     1
    / \
   2   3
    \
     4
"""

# 二叉樹轉列表
values = root.to_list()  # [1, 2, 3, None, 4]

# 手動創建
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
```

## 命令參考

| 命令 | 說明 | 範例 |
|------|------|------|
| `add <id/slug>...` | 添加一個或多個題目 | `python main.py add 1 2 3`<br>`python main.py add two-sum` |
| `list` | 列出所有已添加的題目 | `python main.py list` |
| `search <keyword>` | 按關鍵字搜索題目（標題） | `python main.py search array` |
| `search -t <tag>` | 按標籤搜索題目 | `python main.py search -t "Array"` |
| `stats` | 顯示解題統計 | `python main.py stats` |
| `-h, --help` | 顯示幫助信息 | `python main.py -h` |

## 技術細節

- **API**: 使用 LeetCode 官方 GraphQL API（無需認證，僅獲取公開資訊）
- **數據來源**: leetcode.com（國際版，英文題目）
- **Python 版本**: 3.11+
- **核心依賴**:
  - `requests` - HTTP 請求
  - `rich` - 終端美化輸出

## 常見問題

### Q: 題目描述是英文還是中文？
**A**: 預設為英文（leetcode.com 國際版）。如需中文版本，可修改 `src/leetcode_api.py` 中的 API URL：
```python
GRAPHQL_URL = "https://leetcode.cn/graphql"  # 改為中國版
```

### Q: 如何更新已存在的題目？
**A**: 目前系統會自動跳過已存在的題目。如需重新生成：
1. 刪除 `LeetCodeSolutions/` 中對應的 `.py` 文件
2. 編輯 `data/problems.json`，刪除對應題目的記錄
3. 重新運行 `add` 命令

### Q: 可以自動獲取已提交的代碼嗎？
**A**: 目前版本僅生成空框架和題目描述。如需獲取已提交代碼，需要：
1. 添加 LeetCode 登入認證
2. 使用更高權限的 API 端點
這個功能可能在未來版本中添加。

### Q: 生成的文件可以直接運行嗎？
**A**: 可以！每個文件都包含 `if __name__ == "__main__"` 區塊。添加測試案例後：
```bash
uv run python LeetCodeSolutions/p0001_two_sum.py
```

### Q: 如何添加自己的工具函數？
**A**: 在 `LeetCodeSolutions/utils/` 目錄中添加新的 Python 文件：
```python
# LeetCodeSolutions/utils/helpers.py
def binary_search(arr, target):
    """自定義工具函數"""
    pass

# 在 __init__.py 中導出
from .helpers import binary_search
```

### Q: 題目編號和文件名的對應規則是什麼？
**A**: 文件名格式為 `p{編號}_slug.py`，編號補零到 4 位：
- 題目 1 → `p0001_two_sum.py`
- 題目 15 → `p0015_3sum.py`
- 題目 1000 → `p1000_problem_name.py`

## 開發者指南

如果您想貢獻代碼或修改項目，以下是開發環境設置和代碼規範。

### 開發環境設置

```bash
# 1. 克隆倉庫
git clone <your-repo-url>
cd leetcoder

# 2. 安裝所有依賴（包括開發依賴）
uv sync --dev

# 3. 運行代碼檢查
uv run ruff check .

# 4. 自動修復代碼問題
uv run ruff check --fix .

# 5. 格式化代碼
uv run ruff format .
```

### 代碼規範

本項目使用 [Ruff](https://github.com/astral-sh/ruff) 作為代碼檢查和格式化工具。

**Ruff 配置：**
- 行長度限制：100 字符
- Python 版本：3.11+
- 啟用的規則：pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear 等

**提交前檢查：**
```bash
# 檢查代碼規範
uv run ruff check .

# 格式化代碼
uv run ruff format .
```

**特殊說明：**
- `LeetCodeSolutions/` 目錄名保持駝峰命名（面向用戶）
- 生成的題目文件中的函數名保持 LeetCode 原始命名（如 `twoSum`）
- 這些例外已在 `pyproject.toml` 中配置

### 項目結構說明

```
src/
├── leetcode_api.py        - LeetCode GraphQL API 封裝
├── solution_generator.py  - 題目文件生成邏輯
└── problem_index.py       - 本地題目索引管理

LeetCodeSolutions/         - 用戶解題目錄
└── utils/                 - 通用數據結構（ListNode, TreeNode）
```

### 添加新功能

1. 在相應的模組中添加功能
2. 運行 ruff 檢查和格式化
3. 更新 README 文檔
4. 提交 Pull Request

## 開發計劃

未來可能添加的功能：

- [ ] 支持中英文題目切換（配置選項）
- [ ] 添加 LeetCode 認證，自動獲取已提交代碼
- [ ] 支持更多編程語言（Java, C++, Go, JavaScript 等）
- [ ] 添加題目難度篩選功能
- [ ] 生成學習進度報告和可視化圖表
- [ ] 支持題目標籤分類查看
- [ ] 添加每日一題提醒功能
- [ ] 導出為 Markdown 筆記

## 貢獻

歡迎提交 Issue 和 Pull Request！

### 提交 Issue

如有任何問題或建議，請：
1. 在 GitHub 創建 Issue
2. 描述問題或功能需求
3. 提供相關的錯誤信息或使用場景
4. 如果是 bug，請包含復現步驟

### 提交 Pull Request

1. Fork 本倉庫
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

**注意：** 提交前請確保代碼通過 ruff 檢查：
```bash
uv run ruff check .
uv run ruff format .
```

## 相關資源

- [LeetCode 官網](https://leetcode.com/)
- [LeetCode 中文版](https://leetcode.cn/)
- [Ruff - Python Linter](https://github.com/astral-sh/ruff)
- [uv - Python Package Manager](https://github.com/astral-sh/uv)
- [Rich - Python Terminal](https://github.com/Textualize/rich)

## 致謝

- 感謝 [LeetCode](https://leetcode.com/) 提供優質的算法題目平台
- 感謝 [Astral](https://astral.sh/) 開發的 uv 和 ruff 工具
- 感謝所有貢獻者和使用者的反饋

## License

MIT License

Copyright (c) 2025 LeetCoder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<div align="center">

**Happy Coding! 祝刷題順利！** 🚀

Made with ❤️ by LeetCode enthusiasts

</div>
