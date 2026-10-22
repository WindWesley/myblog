---
title: Charles 抓不到请求，先查代理，再查证书
date: 2026-08-28
category: 调试排障
author: 阅读整理
draft: false
---


手机浏览器能被 Charles 抓到，不代表 App 的所有请求都会经过同一条代理链路。先确定请求由谁发出：Dio 的 IO 适配器、WebView，还是原生 SDK。它们未必使用同一套代理配置。

## 看不到连接，先别改证书

Charles 完全没有连接记录时，优先确认手机能否访问电脑的代理端口、Charles 是否允许连接、设备与电脑的网络是否互通，然后确认当前客户端是否实际走了代理。

dart:io 的 HttpClient 默认代理逻辑基于环境配置，不应假设它自动读取手机 Wi-Fi 设置里的代理。Dio 还可以更换适配器，所以“Dio 一定怎样”也不够准确。[HttpClient 文档](https://api.dart.dev/dart-io/HttpClient-class.html)

以下是 Dio 5 的 IO 调试配置片段。需要在发起请求前使用；不适用于 Web。代理地址由调试构建参数提供，不写死在业务代码里：

```dart
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';

Dio createDio() {
  final dio = Dio();
  const proxy = String.fromEnvironment('DEBUG_HTTP_PROXY');
  if (kDebugMode && proxy.isNotEmpty) {
    dio.httpClientAdapter = IOHttpClientAdapter(
      createHttpClient: () => HttpClient()
        ..findProxy = (_) => 'PROXY $proxy',
    );
  }
  return dio;
}
```

例如调试时传入 `--dart-define=DEBUG_HTTP_PROXY=192.168.1.100:8888`，地址应换成当前电脑可达的地址。这个片段只配置代理，保留默认的证书验证，并不承诺此时 HTTPS 正文已经能解密。当前 IOHttpClientAdapter 提供 createHttpClient，旧回调已标记弃用。[适配器 API](https://pub.dev/documentation/dio/latest/io/IOHttpClientAdapter/IOHttpClientAdapter.html)

## 有连接，才能继续排查 TLS

能看到 CONNECT 隧道却没有 HTTPS 正文时，检查目标域名是否启用了 SSL Proxying，再检查调试客户端是否信任 Charles CA。还要考虑证书固定、自定义信任逻辑和具体平台配置。

不要把 badCertificateCallback 无条件返回 true 当成通用解法。需要自定义信任时，应只在调试环境使用受控的 SecurityContext，添加明确的调试 CA，同时保留正常证书验证。

原文把 Flutter 的根证书来源概括为与系统仓库完全无关，这并不准确。Dart 文档说明，macOS、iOS 和 Android 的默认可信根来源于平台内置证书仓库；这也不等于用户安装的任意 CA 必然被当前客户端接受。[SecurityContext.defaultContext](https://api.dart.dev/dart-io/SecurityContext/defaultContext.html)

## 工具能减少配置，不能取消验证

原文推荐的调试插件是否支持当前平台、适配器和证书策略，需要核查具体版本。仅凭“一行代码”不能认定发布包绝无影响。

VPN 类工具同样不天然解决 HTTPS 解密。流量经过工具，与工具能够读取明文，是两个条件；TLS 信任和证书固定仍可能阻止解密。

最后用发布构建确认：没有调试代理，没有放宽证书校验，也没有输出 Token 或密码的网络日志。排查路径清楚以后，抓包失败就能落到具体层，而不必反复猜是不是 Dio 出了问题。
