# AndroidHardcodedStringExtractor
Android Hardcoded String Extractor


1. 配合`rigrep` 或者 `ack` 搜索出需要extract的地方

    explamples:

    搜索代码中的中文string:    `rg '".*[\u4e00-\u9fa5].*"' -tjava -tkotlin --line-number > grep_file.txt`

    搜索layout文件中的string:   `rg 'android:text=' > grep_file.txt`

2. 手动检查删除不需要的行，暂时不能精确的搜索出来

3. `python3 AndroidHardedcodeStringExtractor.py`

4. 剩下靠勤劳的双手
