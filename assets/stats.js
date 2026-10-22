// Only count the published blog; local previews do not affect production totals.
(() => {
  if (location.hostname !== 'windwesley.github.io' ||
      !location.pathname.startsWith('/myblog/')) return;
  const script = document.createElement('script');
  script.src = 'https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
  script.async = true;
  document.head.appendChild(script);
})();
