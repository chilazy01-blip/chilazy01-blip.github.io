(() => {
  'use strict';
  const sections = [...document.querySelectorAll('.report-section')];
  const navLinks = [...document.querySelectorAll('.site-header nav a')];
  const presentButton = document.getElementById('present');
  const bar = document.querySelector('.presentation-bar');
  const announcer = document.getElementById('announcer');
  let presenting = false;
  let active = 0;

  document.querySelectorAll('#present, #print, .filters, .viewer-tabs').forEach(el => el.hidden = false);

  function setNav(index) {
    active = index;
    navLinks.forEach((link, i) => {
      if (link.hash === '#' + sections[index].id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    document.getElementById('presentation-position').textContent = `${String(index + 1).padStart(2, '0')} / ${String(sections.length).padStart(2, '0')} · ${sections[index].dataset.label}`;
    document.getElementById('prev-section').disabled = index === 0;
    document.getElementById('next-section').disabled = index === sections.length - 1;
  }

  function revealTarget(target) {
    let node = target;
    while (node) {
      if (node.tagName === 'DETAILS') node.open = true;
      node = node.parentElement;
    }
  }

  function showSection(index, scroll = true) {
    if (index < 0 || index >= sections.length) return;
    setNav(index);
    if (presenting) {
      sections.forEach((section, i) => section.hidden = i !== index);
      document.querySelectorAll('video').forEach(video => {
        if (video.closest('.report-section') !== sections[index]) video.pause();
      });
    }
    if (scroll) sections[index].scrollIntoView({ behavior: 'instant', block: 'start' });
  }

  function setPresentation(enabled) {
    presenting = enabled;
    document.body.classList.toggle('presenting', enabled);
    document.querySelector('.report-update-notice').hidden = enabled;
    presentButton.setAttribute('aria-pressed', String(enabled));
    presentButton.textContent = enabled ? '退出汇报模式' : '汇报模式 ↗';
    bar.hidden = !enabled;
    if (!enabled) sections.forEach(section => section.hidden = false);
    showSection(active);
    announcer.textContent = enabled ? '已开启汇报模式。左右方向键切换部分，Escape 退出。每部分可上下滚动。' : '已恢复完整页面。';
  }

  presentButton.addEventListener('click', () => setPresentation(!presenting));
  document.getElementById('exit-presentation').addEventListener('click', () => setPresentation(false));
  document.getElementById('prev-section').addEventListener('click', () => showSection(active - 1));
  document.getElementById('next-section').addEventListener('click', () => showSection(active + 1));
  document.addEventListener('keydown', event => {
    if (!presenting || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'Escape') { setPresentation(false); return; }
    if (event.target.closest('input,select,textarea,video,[tabindex="0"]')) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); showSection(active + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); showSection(active - 1); }
  });

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (!target) return;
    event.preventDefault();
    revealTarget(target);
    const section = target.closest('.report-section');
    if (section) showSection(sections.indexOf(section), false);
    // Hash navigation also works when the website is opened directly from disk.
    try { history.pushState(null, '', link.getAttribute('href')); } catch (_) { location.hash = link.hash; }
    target.scrollIntoView({ behavior: 'instant', block: 'start' });
  });

  function followHash() {
    const target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    revealTarget(target);
    const section = target.closest('.report-section');
    if (section) showSection(sections.indexOf(section), false);
    target.scrollIntoView({ behavior: 'instant', block: 'start' });
  }
  window.addEventListener('hashchange', followHash);
  window.addEventListener('popstate', followHash);

  let scrollTick = false;
  window.addEventListener('scroll', () => {
    if (scrollTick) return;
    scrollTick = true;
    requestAnimationFrame(() => {
      if (!presenting) {
        let index = 0;
        sections.forEach((section, i) => { if (section.getBoundingClientRect().top <= 160) index = i; });
        setNav(index);
      }
      const max = document.documentElement.scrollHeight - innerHeight;
      document.querySelector('.reading-progress span').style.width = `${max > 0 ? Math.min(100, scrollY / max * 100) : 0}%`;
      scrollTick = false;
    });
  }, { passive: true });

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
  setNav(0);
  followHash();
})();
