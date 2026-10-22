---
title: 图片还没加载出来，列表的高度就应该确定了
date: 2023-11-23
category: 组件设计
author: Wesley
excerpt: 占位图、原图和错误图共享同一块布局空间，滚动才不会被图片尺寸牵着走。
draft: false
---

头像从灰色占位变成真实图片，通常很平稳；聊天里的长图加载出来，却可能把正在阅读的消息顶走。两者最大的区别，往往是尺寸是否提前确定。

项目的 `custom_image.dart` 已经统一了本地图片、SVG、网络图片和代币图标的入口。业务页面只传地址、宽高、圆角，这比到处写加载占位与失败回退更容易维护。

接着值得统一的，是三个状态共用的外框：加载中、成功、失败，都不应该自行决定不同的尺寸。

下面是一个普通网络缩略图的改进示例。省略了项目的域名转换和缓存选择，重点只放在布局；需要 `material.dart`：

```dart
class StableNetworkImage extends StatelessWidget {
  const StableNetworkImage({
    super.key,
    required this.url,
    required this.width,
    required this.height,
  });

  final String url;
  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    Widget placeholder() => const ColoredBox(color: Color(0xFFE9E9E9));
    return SizedBox(
      width: width,
      height: height,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: url.trim().isEmpty
            ? placeholder()
            : Image.network(
                url,
                fit: BoxFit.cover,
                loadingBuilder: (_, child, progress) =>
                    progress == null ? child : placeholder(),
                errorBuilder: (_, __, ___) => const ColoredBox(
                  color: Color(0xFFE9E9E9),
                  child: Center(child: Icon(Icons.broken_image_outlined)),
                ),
              ),
      ),
    );
  }
}
```

宽高应当是有限正数。头像可以固定为正方形；消息图片则可以根据服务端宽高，先计算一个受最大宽高约束的展示矩形。服务端没有尺寸时，采用明确的默认比例，接受必要的一次布局调整。

### 图片地址也需要一个解释入口

网络 URL、本地路径、内存图片不是同一种数据。IM 的图片显示逻辑已经区分这些来源，但点击预览也要沿用同一套分类，不能把“不是网络地址”全部当成本地文件。

更稳妥的方式是在解析消息时确定图片来源，再让缩略图和大图预览共享结果。base64 解码失败应作为无效图片处理，而不是让异常穿到列表构建过程中。

最后，统一图片组件并不意味着统一缓存。v4 的普通网络图实际走 `ExtendedImage`，代币图标走 `CachedNetworkImage`。确定需要哪一种缓存策略后，再替换内部实现；页面的尺寸和失败表现可以保持不变。
