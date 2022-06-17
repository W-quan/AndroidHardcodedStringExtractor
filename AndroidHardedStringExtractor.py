import os,re, hashlib

'''
Android Hardcoded String Extractor

1. 配合`rigrep` 或者 `ack` 搜索出需要extract的地方

    explamples:

    搜索代码中的中文string:    `rg '".*[\u4e00-\u9fa5].*"' -tjava -tkotlin --line-number > grep_file.txt`

    搜索layout文件中的string:   `rg 'android:text=' > grep_file.txt`

2. 手动检查删除不需要的行，暂时不能精确的搜索出来

3. `python3 AndroidHardedcodeStringExtractor.py`

4. 剩下靠勤劳的双手

'''

# rg/ack 搜索生成的文件
grep_file = 'grep_file.text'

project_path = '/Users/wzq/Workspace/Android/Ermeng_Android_Client/'
strings_file = f'{project_path}app/src/main/res/values/strings.xml'

# rg/ack 搜索出来的文件， 内容分隔符
split_pattern = r'    +'

# 匹配string，不兼容存在 \" 的情况
# text_pattern = r'"[^"]+"'

# 匹配string，兼容存在 \" 的情况
string_pattern = r'"[^"\\]*(?:\\[\s\S][^"\\]*)*"'

key_prefix = 'md5_'

# strings.xml key去重
stringDict = {}

# 代码导入，还不能导入R文件, 因为可能不同module有不同R文件。暂时靠IDE
importTextKt = '\nimport com.ormatch.android.asmr.app.ELContext\n'
importTextJava = '\nimport com.ormatch.android.asmr.app.ELContext;\n'

def insertImport(filePath):
    with open(filePath, 'r+') as f:
        contents = f.readlines()
        if 'import com.ormatch.android.asmr.app.ELContext' in contents[2]:
            print('already imported')
            return 

        if '.java' in filePath:
            contents.insert(1, importTextJava)
        elif '.kt' in filePath:
            contents.insert(1, importTextKt)

        f.seek(0)
        f.writelines(contents)


def extractJavaFileString(filePath, line, key, text):
    with open(filePath, 'r+') as f:
        contents = f.readlines()
        contents[line] = contents[line].replace(text, f'ELContext.getContext().getString(R.string.{key})')
        f.seek(0)
        f.writelines(contents)

def extractKotlinFileString(filePath, line, key, text):
    with open(filePath, 'r+') as f:
        contents = f.readlines()
        contents[line] = contents[line].replace(text, f'ELContext.context?.getString(R.string.{key})')
        f.seek(0)
        f.writelines(contents)

def replaceCodeFileString(filePath, line, key, text):
    insertImport(filePath)

    # 插入了import语句，加2行
    line = line + 2

    if '.java' in filePath:
        extractJavaFileString(filePath, line, key, text)
    elif '.kt' in filePath:
        extractKotlinFileString(filePath, line, key, text)


def replaceLayoutFileHardcodedString(filePath, line, regex, key):
    f = open(filePath,"r")
    lines = f.readlines()
    lines[line] = lines[line].replace(regex, f'@string/{key}')
    print(lines[line])

    f = open(filePath, 'w+')
    f.writelines(lines)
    f.close()

def extractString(key, value):
    if key in stringDict:
        print(f'重复的key: {key} {value}')
        return

    file = open(strings_file, "a+")
    line = f'    <string name="{key_prefix + key}">{value}</string>\n'
    file.write(line)
    file.flush()
    file.close()

    stringDict[key] = value

# 只是计数的
count = 0

for line in open("grep_file.txt"): 
    print('\n\n==========================\n\n')
    print(count)
    count += 1
    print(line),  

    # 文件名 文案分割
    array = re.split(split_pattern, line)

    file_split = array[0].split(':')
    filePath = project_path + file_split[0]
    line = int(file_split[1]) - 1

    # 文案
    textList = re.compile(string_pattern).findall(array[1])
    for string in textList:
        # 文案md5
        text = string.strip('"')
        hl = hashlib.md5()
        hl.update(text.encode('utf-8'))
        md5 = hl.hexdigest()

        # 提取文案写入strings.xml
        extractString(md5, text)

        # 替换layout文件中的文案
        if '.xml' in file_split[0]:
            replaceLayoutFileHardcodedString(filePath, line, text, key_prefix + md5)

        # 替换代码中的Hardcoded string
        replaceCodeFileString(filePath, line, key_prefix + md5, string)

