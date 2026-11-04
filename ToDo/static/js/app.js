// Todo — небольшие интерактивные улучшения. Всё работает и без JS, тут только анимации.
(function () {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const wait = (ms) => new Promise((r) => setTimeout(r, reduceMotion ? 0 : ms));

  // ---------- Уведомления: закрытие и автоскрытие ----------
  function hideToast(t) {
    t.classList.add('hide');
    setTimeout(() => t.remove(), 300);
  }
  document.querySelectorAll('.toast-todo').forEach((t, i) => {
    t.querySelector('.t-close')?.addEventListener('click', () => hideToast(t));
    setTimeout(() => hideToast(t), 4000 + i * 400);
  });

  // ---------- Отметка задачи: галочка «пружинит», карточка уезжает, потом отправка ----------
  document.querySelectorAll('.toggle-form').forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('.task-check');
      const card = form.closest('.task-card');
      if (card && !card.classList.contains('is-done')) {
        btn.classList.add('checking');
        card.classList.add('striking');
        await wait(450);
      }
      card?.classList.add('leaving');
      await wait(300);
      form.submit();
    });
  });

  // ---------- Удаление: подтверждение + анимация ухода ----------
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!confirm(form.dataset.confirm)) return;
      form.closest('.task-card, .project-card')?.classList.add('leaving');
      await wait(350);
      form.submit();
    });
  });

  // ---------- Числа «набегают» от 0 ----------
  document.querySelectorAll('[data-count]').forEach((el) => {
    const target = parseInt(el.dataset.count, 10) || 0;
    if (reduceMotion || target === 0) { el.textContent = target; return; }
    const duration = 900;
    const start = performance.now();
    function step(now) {
      const p = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });

  // ---------- Кнопка отправки формы: защита от двойного клика ----------
  document.querySelectorAll('form.form-card-form').forEach((form) => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.insertAdjacentHTML('afterbegin', '<span class="spinner-border spinner-border-sm"></span>');
      }
    });
  });
})();
