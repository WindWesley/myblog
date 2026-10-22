# 开发笔记：工具、数据与聊天交互

这次重写共 15 篇。以具体开发场景为主，原实现中可复用的部分继续保留，需要调整的地方在文中给出改法。示例不代表已经修改原项目。

## 工具封装

- [给 List 加方法之前，先想清楚它会不会改原数据](list-extensions.md)
- [接口字段一会儿是数字，一会儿是字符串，MapEx 应该兜到哪里](map-parsing.md)
- [确认框关掉以后，业务代码才开始](dialog-results.md)

## 组件设计

- [图片还没加载出来，列表的高度就应该确定了](image-layout.md)
- [聊天列表套两层滚动，方便的是布局，麻烦的是后面](im-one-scroll-view.md)

## 架构思路

- [新增一个接口，不应该顺便重写一次网络请求](request-boundaries.md)
- [HTTP 200 之后，错误处理才走了一半](response-errors.md)
- [聊天历史加载，除了 loading 还需要什么](im-history-pagination.md)
- [消息气泡可以换样式，消息身份不能跟着换](im-message-state.md)

## 数据存储

- [没网时还能打开页面，需要怎样一份缓存](cache-readable-pages.md)
- [SPManager 最该管的，其实是默认值和旧数据](preferences-migration.md)

## 交互实现

- [聊天列表里插日期，不要在 itemBuilder 里数消息](im-timeline-rows.md)
- [收到新消息，不一定要滚到底部](im-follow-new-messages.md)
- [加载历史消息时，别让正在看的那一行跑掉](im-history-anchor.md)
- [点一条引用，为什么定位消息不只是 scrollTo](im-message-navigation.md)

## 使用

文章已经同步到本地博客的 `content/posts/`，替换上一批草稿。全部保留 `draft: true`，未上传 GitHub；发布前修改日期、署名及草稿标记即可。代码片段需要按文中前提接入，展示代码与原项目代码已作区分。

技术核对和验证范围见 [写作依据](writing-notes.md)。
