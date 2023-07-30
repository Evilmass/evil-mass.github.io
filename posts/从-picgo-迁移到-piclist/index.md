# 从 PicGo 迁移到 PicList


## 理由
作为一个图片上传工具，其实没有这么多要求。但是 PicList 恰好有两给痛点无法解决：
1. 无法同步删掉图床的图片
2. 上传图片只能拖拽图片到主窗口

图片一多容易冗余。
窗口一多（vscode 代码窗口、osbidian 写作窗口、Chrome 网页、PicGo 主窗口、图片文件夹窗口），切换图片文件夹到上传窗口略麻烦。

而 [PicList](https://github.com/Kuingsmile/PicList) 正好解决以上痛点。
![](https://s2.loli.net/2023/07/22/2589jiX7uYMGTdB.png)

## 从 PicGo 一键迁移
![](https://s2.loli.net/2023/07/22/alspAJ83v7W1oLu.png)

## Mini 窗口快速上传
只要往窗口拖拽图片即可，常用且实用的功能。
![](https://s2.loli.net/2023/07/22/p3wsJEFLoQqghnW.png)

## 添加水印和去除敏感信息
水印看情况加，但公开访问的图片不建议带任何个人隐私，所以消除图片里面的 EXIF 数据很有必要。
![](https://s2.loli.net/2023/07/22/SZDgUiHKkon7fT8.png)

## 同步配置到 Github 私人仓库
![](https://s2.loli.net/2023/07/22/pQn32ZicbuRHtNU.png)

## 关闭声音通知
有个窗口提示即可，不然批量上传后会一直有声音提示。
![](https://s2.loli.net/2023/07/22/RCb6lDYehHBNVwf.png)


功能稳定之后一般就不再升级版本了，除非有 Bug。

我在 1.9.7 版本提了一个[功能需求](https://github.com/Kuingsmile/PicList/discussions/71#discussioncomment-6495535)也马上加上了，整挺好。 
