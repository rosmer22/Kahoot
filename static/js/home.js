
(() => {
  const track = document.getElementById('carousel-track');
  const prev = document.querySelector('.carousel .prev');
  const next = document.querySelector('.carousel .next');
  const viewport = document.querySelector('.carousel-viewport');
  if (!track || !viewport) return;
  const items = Array.from(track.children);
  let index = 0, itemWidth = 0;

  function measure(){
    const first = items[0]; if (!first) return;
    const gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 0;
    itemWidth = first.getBoundingClientRect().width + gap;
  }
  function snap(i){
    index = Math.max(0, Math.min(i, items.length - 1));
    const maxT = (items.length * itemWidth) - viewport.getBoundingClientRect().width;
    const raw = index * itemWidth;
    const x = Math.max(0, Math.min(raw, maxT));
    track.style.transform = `translateX(${-x}px)`;
    items.forEach((el, idx) => el.setAttribute('aria-selected', idx === index ? 'true' : 'false'));
  }
  function step(dir){
    const visible = Math.max(1, Math.round(viewport.getBoundingClientRect().width / itemWidth));
    snap(index + dir * visible);
  }
  prev && prev.addEventListener('click', () => step(-1));
  next && next.addEventListener('click', () => step(1));
  viewport.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') step(-1);
    if (e.key === 'ArrowRight') step(1);
  });
  let sx=0,cx=0,drag=false,base=0;
  function cur(){
    const t = getComputedStyle(track).transform;
    if (t && t !== 'none'){ const m = new DOMMatrixReadOnly(t); return m.m41; }
    return 0;
  }
  function start(x){ drag=true; sx=cx=x; base=cur(); track.style.transition='none'; }
  function move(x){ if(!drag) return; cx=x; const d=cx-sx; track.style.transform=`translateX(${base+d}px)`; }
  function end(){ if(!drag) return; drag=false; track.style.transition=''; const d=cx-sx; if (Math.abs(d) > itemWidth*0.3){ step(d>0?-1:1); } else { snap(index); } }
  viewport.addEventListener('mousedown', e=>start(e.clientX));
  window.addEventListener('mousemove', e=>move(e.clientX));
  window.addEventListener('mouseup', end);
  viewport.addEventListener('touchstart', e=>start(e.touches[0].clientX), {passive:true});
  window.addEventListener('touchmove', e=>move(e.touches[0].clientX), {passive:true});
  window.addEventListener('touchend', end);
  const ro = new ResizeObserver(()=>{ measure(); snap(index); });
  ro.observe(viewport);
  measure(); snap(0);
})();
