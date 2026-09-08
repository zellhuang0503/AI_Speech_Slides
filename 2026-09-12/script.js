/* ==========================================================================
   梵亞行銷 AI 專題簡報系統控制指令碼
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // DOM 元素選取
  const slides = document.querySelectorAll('.slide');
  const progressBar = document.getElementById('progress-bar');
  const controlPanel = document.getElementById('control-panel');
  const slideNumberText = document.getElementById('slide-number');
  
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnTheme = document.getElementById('btn-theme');
  const btnNotes = document.getElementById('btn-notes');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  
  const zonePrev = document.getElementById('zone-prev');
  const zoneNext = document.getElementById('zone-next');
  
  const notesPanel = document.getElementById('notes-panel');
  const btnNotesClose = document.getElementById('btn-notes-close');
  const noteContent = document.getElementById('note-content');
  
  // 簡報狀態
  let currentSlideIndex = 0; // 0-based
  const totalSlides = slides.length;
  let panelTimeout = null;

  // 調整簡報舞台等比縮放
  function adjustSlideScale() {
    const stage = document.querySelector('.slides-stage');
    if (!stage) return;
    
    const baseWidth = 1200;
    const baseHeight = 900;
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    const scaleX = windowWidth / baseWidth;
    const scaleY = windowHeight / baseHeight;
    const scale = Math.min(scaleX, scaleY);
    
    stage.style.transform = `scale(${scale})`;
  }

  // 初始化
  function init() {
    // 進行舞台縮放調整
    adjustSlideScale();
    
    // 優先從 URL Hash 讀取頁碼 (e.g. #3 表示第 3 頁，即 index = 2)
    const hash = window.location.hash;
    if (hash && hash.startsWith('#slide-')) {
      const pageNum = parseInt(hash.replace('#slide-', ''), 10);
      if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalSlides) {
        currentSlideIndex = pageNum - 1;
      }
    }
    
    // 渲染第一頁與小抄
    showSlide(currentSlideIndex);
    triggerPanelFlash();
    
    // 註冊事件監聽
    setupEventListeners();
  }

  // 顯示指定投影片
  function showSlide(index) {
    // 邊界檢查
    if (index < 0) index = 0;
    if (index >= totalSlides) index = totalSlides - 1;
    
    // 移除舊的 active
    slides.forEach(slide => slide.classList.remove('active'));
    
    // 設定新的 active
    currentSlideIndex = index;
    slides[currentSlideIndex].classList.add('active');
    
    // 更新 URL Hash (但不觸發 hashchange 以免循環)
    history.replaceState(null, null, `#slide-${currentSlideIndex + 1}`);
    
    // 更新控制面板
    slideNumberText.textContent = `${currentSlideIndex + 1} / ${totalSlides}`;
    
    // 更新進度條 (第一頁是 0%，最後一頁是 100%)
    const pct = totalSlides > 1 ? (currentSlideIndex / (totalSlides - 1)) * 100 : 0;
    progressBar.style.width = `${pct}%`;
    
    // 更新演講者小抄內容
    updateNotes();
    
    // 每次切換，控制面板亮起提示
    triggerPanelFlash();
  }

  // 下一頁
  function nextSlide() {
    if (currentSlideIndex < totalSlides - 1) {
      showSlide(currentSlideIndex + 1);
    } else {
      // 最後一頁的特效或提示 (可擴充)
      console.log('已經是最後一頁');
    }
  }

  // 上一頁
  function prevSlide() {
    if (currentSlideIndex > 0) {
      showSlide(currentSlideIndex - 1);
    }
  }

  // 更新小抄內容
  function updateNotes() {
    const slideId = currentSlideIndex + 1;
    const noteSource = document.querySelector(`#notes-database [data-note-for="${slideId}"]`);
    
    if (noteSource) {
      noteContent.innerHTML = noteSource.innerHTML;
    } else {
      noteContent.innerHTML = '<p>本頁無演講備忘錄。</p>';
    }
  }

  // 切換演講者小抄面版
  function toggleNotesPanel() {
    notesPanel.classList.toggle('active');
    btnNotes.classList.toggle('active');
  }

  // 切換亮暗色主題
  function toggleTheme() {
    const isLight = document.body.classList.toggle('light-theme');
    document.body.classList.toggle('dark-theme', !isLight);
    
    // 切換按鈕圖案
    const themeIcon = btnTheme.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.textContent = isLight ? '☾' : '☼';
    }
  }

  // 切換全螢幕
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.error(`無法進入全螢幕模式: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  }

  // 使控制面板短暫亮起
  function triggerPanelFlash() {
    controlPanel.classList.add('panel-active');
    
    if (panelTimeout) {
      clearTimeout(panelTimeout);
    }
    
    // 2.5 秒後如果沒有滑鼠在其上，則自動淡出
    panelTimeout = setTimeout(() => {
      // 只有在滑鼠沒有 hover 在上面時才淡出
      if (!controlPanel.matches(':hover')) {
        controlPanel.classList.remove('panel-active');
      }
    }, 2500);
  }

  // 設定事件監聽器
  function setupEventListeners() {
    // 1. 鍵盤事件監聽
    document.addEventListener('keydown', (e) => {
      // 避免在輸入框等元素內誤觸
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        return;
      }
      
      switch (e.key) {
        case 'ArrowRight':
        case 'ArrowDown':
        case 'PageDown':
        case ' ':
        case 'Enter':
          e.preventDefault();
          nextSlide();
          break;
        case 'ArrowLeft':
        case 'ArrowUp':
        case 'PageUp':
        case 'Backspace':
          e.preventDefault();
          prevSlide();
          break;
        case 'p':
        case 'P':
          e.preventDefault();
          toggleNotesPanel();
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          toggleFullscreen();
          break;
      }
    });

    // 2. 控制面板按鈕點擊
    btnPrev.addEventListener('click', (e) => {
      e.stopPropagation();
      prevSlide();
    });
    
    btnNext.addEventListener('click', (e) => {
      e.stopPropagation();
      nextSlide();
    });
    
    btnTheme.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleTheme();
    });
    
    btnNotes.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleNotesPanel();
    });
    
    btnFullscreen.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleFullscreen();
    });

    // 3. 點擊熱區 (左右側點擊切換)
    zonePrev.addEventListener('click', prevSlide);
    zoneNext.addEventListener('click', nextSlide);

    // 4. 小抄面板關閉按鈕
    btnNotesClose.addEventListener('click', toggleNotesPanel);

    // 5. 滑鼠在控制面板 hover 時防止淡出
    controlPanel.addEventListener('mouseenter', () => {
      controlPanel.classList.add('panel-active');
      if (panelTimeout) clearTimeout(panelTimeout);
    });
    
    controlPanel.addEventListener('mouseleave', () => {
      triggerPanelFlash();
    });

    // 6. 支援手機/平板觸控手勢滑動
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
      const swipeDistance = touchEndX - touchStartX;
      const threshold = 50; // 滑動門檻 (px)
      
      if (swipeDistance < -threshold) {
        // 向左滑 -> 下一頁
        nextSlide();
      } else if (swipeDistance > threshold) {
        // 向右滑 -> 上一頁
        prevSlide();
      }
    }

    // 7. 全螢幕狀態同步 (例如使用者手動按 Esc 退出時更新按鈕圖案)
    document.addEventListener('fullscreenchange', () => {
      if (document.fullscreenElement) {
        btnFullscreen.style.color = 'var(--accent-green)';
      } else {
        btnFullscreen.style.color = '';
      }
    });

    // 8. 視窗 Hash 改變時同步投影片 (例如點瀏覽器上一頁/下一頁)
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash;
      if (hash && hash.startsWith('#slide-')) {
        const pageNum = parseInt(hash.replace('#slide-', ''), 10);
        if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalSlides) {
          if (pageNum - 1 !== currentSlideIndex) {
            showSlide(pageNum - 1);
          }
        }
      }
    });

    // 9. 監聽視窗 resize，進行等比縮放
    window.addEventListener('resize', adjustSlideScale);
  }

  // 執行初始化
  init();
});
