# 搭建一个属于自己的在线网盘


简单记录搭建 [onedrive-vercel-index](https://github.com/spencerwooo/onedrive-vercel-index) 的过程。

[官方文档](https://ovi.swo.moe/zh/docs/getting-started)的搭建流程清晰明了，跟着步骤来就行，唯一问题是官方仓库的 [clientID 过期](https://github.com/spencerwooo/onedrive-vercel-index/issues/1049)。


参考[使用你自己的 client id 与 secret](https://ovi.swo.moe/zh/docs/advanced#%E4%BD%BF%E7%94%A8%E4%BD%A0%E8%87%AA%E5%B7%B1%E7%9A%84-client-id-%E4%B8%8E-secret) 修改自己 fork 的仓库下 [api.config.js](https://github.com/spencerwooo/onedrive-vercel-index/blob/main/config/api.config.js)

```js
module.exports = {
  // The clientId and clientSecret are used to authenticate the user with Microsoft Graph API using OAuth. You would
  // not need to change anything here if you can authenticate with your personal Microsoft account with OneDrive International.
  clientId: 'd87bcc39-1750-4ca0-ad54-f8d0efbb2735',
  obfuscatedClientSecret: 'U2FsdGVkX1830zo3/pFDqaBCVBb37iLw3WnBDWGF9GIB2f4apzv0roemp8Y+iIxI3Ih5ecyukqELQEGzZlYiWg==',
  ...
}
```

最后在 vercel dashboard 再设置下自定义域名，完美。

因为仓库用的是 LocalStorage 的方式，所以 .password 这种方法的不能完全保证安全性，感觉使用 github 的 env 变量这类方法更合适。

作者早期的 [onedrive-cf-index](https://github.com/spencerwooo/onedrive-cf-index) 套用了 cloudflare，理论上在现有仓库手动反代一下效果更好。但挂载流媒体行为会[违反 cf 的 tos](https://hostloc.com/thread-1053006-1-1.html)，所以还是不折腾了。

各路人士薅了这么久 cf 羊毛，cf 还是财大气粗的提供各种优质服务，respct。

最后放效果图
![](https://s2.loli.net/2023/06/27/hyzdAln4emxB5EL.png)


不挂梯子的直链速度还可以，播放视频绰绰有余了
![](https://s2.loli.net/2023/06/27/7w1WndxBTkFZgqX.jpg)
