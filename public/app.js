(() => {
  'use strict';
  const groups = [...document.querySelectorAll('.report-group')];
  const sections = [...document.querySelectorAll('.report-section')];
  const navLinks = [...document.querySelectorAll('.site-header nav a')];
  const pageLinks = [...document.querySelectorAll('[data-page-link]')];
  const presentButton = document.getElementById('present');
  const bar = document.querySelector('.presentation-bar');
  const readingControls = document.querySelector('.reading-controls');
  const announcer = document.getElementById('announcer');
  let presenting = false;
  let activeSection = document.getElementById(groups[0].dataset.entry);

  document.querySelectorAll('#present, #print, .filters, .viewer-tabs').forEach(el => el.hidden = false);
  document.body.classList.add('navigation-ready');

  function scope() {
    const group = activeSection.closest('.report-group');
    const pages = [...group.querySelectorAll('.report-section')];
    return {group, pages, index: pages.indexOf(activeSection)};
  }

  function setNav() {
    const {group, pages, index} = scope();
    navLinks.forEach(link => {
      if (link.dataset.reportGroup === group.id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    pageLinks.forEach(link => {
      if (link.hash === '#' + activeSection.id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    const selected = group.querySelector('[data-page-link][aria-current]');
    if (selected) {
      const nav = selected.parentElement;
      const bounds = nav.getBoundingClientRect();
      const linkBounds = selected.getBoundingClientRect();
      if (linkBounds.left < bounds.left) nav.scrollLeft -= bounds.left - linkBounds.left;
      else if (linkBounds.right > bounds.right) nav.scrollLeft += linkBounds.right - bounds.right;
    }
    const position = `${group.dataset.label}${group.dataset.topic ? ' · ' + group.dataset.topic : ''}　${index + 1} / ${pages.length}`;
    document.getElementById('presentation-position').textContent = position;
    document.getElementById('reading-position').textContent = position;
    for (const id of ['prev-section', 'reading-prev']) document.getElementById(id).disabled = index === 0;
    for (const id of ['next-section', 'reading-next']) document.getElementById(id).disabled = index === pages.length - 1;
    readingControls.hidden = presenting;
  }

  function revealTarget(target) {
    let node = target;
    while (node) {
      if (node.tagName === 'DETAILS') node.open = true;
      node = node.parentElement;
    }
  }

  function showSection(section, scroll = true) {
    if (!section) return;
    activeSection = section;
    const group = section.closest('.report-group');
    groups.forEach(item => item.hidden = item !== group);
    sections.forEach(item => item.hidden = item !== section);
    document.querySelectorAll('video').forEach(video => {
      if (video.closest('.report-section') !== section) video.pause();
    });
    setNav();
    if (scroll) window.scrollTo({top: 0, behavior: 'instant'});
    announcer.textContent = `${group.dataset.label}，${section.dataset.label}`;
  }

  function navigate(target, updateHistory = true) {
    const section = target.closest('.report-section') ||
      (target.classList.contains('report-group') ? target.querySelector('.report-section') : null);
    if (section) {
      revealTarget(target);
      showSection(section, target === section || target.classList.contains('report-group'));
    }
    if (updateHistory) {
      try { history.pushState(null, '', '#' + target.id); }
      catch (_) { location.hash = target.id; }
    }
    if (!section || target !== section) target.scrollIntoView({behavior: 'instant', block: 'start'});
  }

  function movePage(delta) {
    const {pages, index} = scope();
    if (pages[index + delta]) navigate(pages[index + delta]);
  }

  function setPresentation(enabled) {
    presenting = enabled;
    document.body.classList.toggle('presenting', enabled);
    presentButton.setAttribute('aria-pressed', String(enabled));
    presentButton.textContent = enabled ? '退出汇报模式' : '汇报模式 ↗';
    bar.hidden = !enabled;
    setNav();
    window.scrollTo({top: 0, behavior: 'instant'});
    announcer.textContent = enabled ? '已开启汇报模式。左右方向键在当前栏目内翻页，Escape退出。' : '已恢复阅读模式，当前栏目和页面保持不变。';
  }

  presentButton.addEventListener('click', () => setPresentation(!presenting));
  document.getElementById('exit-presentation').addEventListener('click', () => setPresentation(false));
  for (const id of ['prev-section', 'reading-prev']) document.getElementById(id).addEventListener('click', () => movePage(-1));
  for (const id of ['next-section', 'reading-next']) document.getElementById(id).addEventListener('click', () => movePage(1));
  document.addEventListener('keydown', event => {
    if (!presenting || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'Escape') { setPresentation(false); return; }
    if (event.target.closest('input,select,textarea,video,[tabindex="0"]')) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); movePage(1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); movePage(-1); }
  });

  document.addEventListener('click', event => {
    if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (!target) return;
    event.preventDefault();
    navigate(target);
  });

  function followHash() {
    const target = document.getElementById(location.hash.slice(1));
    if (target && target !== document.getElementById('main')) navigate(target, false);
    else showSection(document.getElementById(groups[0].dataset.entry));
  }
  window.addEventListener('hashchange', followHash);
  window.addEventListener('popstate', followHash);

  let scrollTick = false;
  window.addEventListener('scroll', () => {
    if (scrollTick) return;
    scrollTick = true;
    requestAnimationFrame(() => {
      const max = document.documentElement.scrollHeight - innerHeight;
      document.querySelector('.reading-progress span').style.width = `${max > 0 ? Math.min(100, scrollY / max * 100) : 0}%`;
      scrollTick = false;
    });
  }, {passive: true});

  document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
    const group = button.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach(el => el.setAttribute('aria-pressed', String(el === button)));
    const rows = [...document.querySelectorAll('[data-group]')];
    rows.forEach(row => row.hidden = group !== '全部' && row.dataset.group !== group);
    document.getElementById('filter-status').textContent = `显示 ${rows.filter(row => !row.hidden).length} / ${rows.length} 个比较点 · ${group}`;
  }));

  const sceneDescriptions = {
    rgb: 'RGB 外观：同一最终场景的原生渲染。点击查看原图。',
    depth: '深度预览：光轴 Z 深度的显示图；玻璃记录玻璃表面。点击查看原图。',
    instance: '实例标签：颜色区分场景物体，用于检查可见性与标注。点击查看原图。'
  };
  document.querySelectorAll('[data-scene]').forEach(button => button.addEventListener('click', () => {
    const kind = button.dataset.scene;
    const img = document.getElementById('scene-image');
    img.src = `assets/room-${kind}.png`;
    img.alt = sceneDescriptions[kind];
    document.getElementById('scene-original').href = img.getAttribute('src');
    document.getElementById('scene-caption').textContent = sceneDescriptions[kind];
    document.querySelectorAll('[data-scene]').forEach(el => el.setAttribute('aria-pressed', String(el === button)));
  }));

  document.querySelectorAll('video').forEach(video => video.addEventListener('play', () => {
    document.querySelectorAll('video').forEach(other => { if (other !== video) other.pause(); });
  }));

  document.querySelectorAll('[data-preview]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      const enabled = button.getAttribute('aria-pressed') !== 'true';
      document.getElementById(button.dataset.preview).src = enabled ? button.dataset.gif : button.dataset.poster;
      button.setAttribute('aria-pressed', String(enabled));
      button.textContent = enabled ? '停止动图，查看静帧' : '播放抽帧动图';
    });
  });

  let printingState;
  window.addEventListener('beforeprint', () => {
    printingState = [...document.querySelectorAll('details')].map(el => [el, el.open]);
    printingState.forEach(([el]) => el.open = true);
  });
  window.addEventListener('afterprint', () => {
    if (printingState) printingState.forEach(([el, open]) => el.open = open);
  });
  document.getElementById('print').addEventListener('click', () => window.print());
  followHash();
})();
