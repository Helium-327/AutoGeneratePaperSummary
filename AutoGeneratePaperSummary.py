import SparkApi
import re
import os
from tqdm import tqdm
#以下密钥信息从控制台获取
appid = "xxxxxxxxxxxxxxxxxxxx"     #填写控制台中获取的 APPID 信息
api_secret = "xxxxxxxxxxxxxxxxxxxxxxxx"   #填写控制台中获取的 APISecret 信息
api_key ="xxxxxxxxxxxxxxxxxxxxxxxx"    #填写控制台中获取的 APIKey 信息

#用于配置大模型版本，默认“general/generalv2”
domain = "generalv3"   # v1.5版本
# domain = "generalv2"    # v2.0版本
#云端环境的服务地址
Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v1.5环境的地址
# Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址


text =[]

# length = 0

def getText(role,content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text

def newDir(paperClass):
    dirPath = "./" + paperClass
    import os
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
        print(f"{dirPath} created.")
    else:
        print(f"{dirPath} already exists.")
    return dirPath
    
def getOutline(paperClass, dirPath):
    fileName = f"{paperClass}_Outline.md"
    OutlinePath = os.path.join(dirPath, fileName)
    if not os.path.exists(OutlinePath):
        prompt = f"假设你是一位顶尖高校的研究生导师，我想写一篇关于{paperClass}的研究论文报告，请帮我写一个提纲。" \
                 f"输出内容的开头和结尾不要输出任何内容。一级标题以#开头，二级标题以##开头，三级标题以###开头，四级标题以####开头"
        question = checklen(getText("user", prompt))
        print("星火:", end="")
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        getText("assistant", SparkApi.answer)
        with open(OutlinePath, "a", encoding="utf-8") as f:
            # f.write(f"## 答案\n\n")
            f.write(SparkApi.answer)
            f.write("\n\n")
    else:
        print(f"{OutlinePath} already exists!")
    print("Outline is Finished!")
    return OutlinePath
def getContent(paperClass, dirPath, OutlinePath):
    # Input = input("请输入\n" +"我:")
    fileName = f"{paperClass}研究报告实例(by_AIGC).md"
    path = os.path.join(dirPath, fileName)
    with open(OutlinePath, "r+", encoding="utf-8") as f:
        readlines = f.readlines()

    def getAnswer(subtile):
        for readline in subtile:
            topic = re.sub(r'^[0-9A-Z\.]*', '', readline.strip())
            Input = f"请结合现阶段最新的论文和{paperClass}原论文总结{topic}"
            question = checklen(getText("user", Input))
            SparkApi.answer = ""
            print("星火:", end="")
            SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
            getText("assistant", SparkApi.answer)
            indice = readlines.index(readline)
            readlines.insert(indice + 1, '\t' + SparkApi.answer)
            # if readline.strip().startswith('###'):
            # print('匹配成功')
            print(topic)
        # return readlines

    # title = [readline for readline in readlines if re.match(r"^#[^#]*$", readline.strip())]
    subtitle1 = [readline for readline in readlines if readline.startswith('#')]
    subtitle2 = [readline for readline in readlines if readline.startswith('##')]
    subtitle3 = [readline for readline in subtitle2 if readline.startswith('###')]
    subtitle4 = [readline for readline in subtitle3 if readline.startswith('####')]
    # title = [readline for readline in readlines if re.match(r'^#+$', readline)]
    # print(title)
    if bool(subtitle3) and bool(subtitle4):
        getAnswer(subtitle4)
    elif bool(subtitle3):
        getAnswer(subtitle3)
    else:
        print('找不到主题')
    with open(path, "w", encoding="utf-8") as f:
        for newline in tqdm(readlines):
            f.write(newline)
        print(f"{fileName} is Finished!")


if __name__ == '__main__':
    text.clear()
    paperClass = input("请输入一个您想要生成提纲的论文主题或对象：")
    dirPath = newDir(paperClass)
    OutlinePath = getOutline(paperClass, dirPath)
    # changeFormat(paperClass, dirPath, OutlinePath)
    getContent(paperClass, dirPath, OutlinePath)



