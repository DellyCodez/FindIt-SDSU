const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('is-open', open);
  });
}

const picker = document.querySelector('[data-photo-picker]');
const categorySelect = document.querySelector('#category');
const typeSelect = document.querySelector('#item_type');
if (categorySelect && typeSelect) {
  const updateTypes = () => {
    for (const option of typeSelect.options) {
      if (!option.value) continue;
      const allowed = !categorySelect.value || option.dataset.categories.split(',').includes(categorySelect.value);
      option.disabled = !allowed;
      option.hidden = !allowed;
    }
    if (typeSelect.selectedOptions[0]?.disabled) typeSelect.value = '';
  };
  categorySelect.addEventListener('change', updateTypes);
  updateTypes();
}

const camera = document.querySelector('[data-camera-picker]');
const previews = document.querySelector('[data-photo-previews]');
const photoError = document.querySelector('[data-photo-client-error]');
if (picker && camera && previews && photoError) {
  let selected = [];
  const showError = (message) => {
    photoError.textContent = message;
    photoError.hidden = !message;
  };
  const render = () => {
    const transfer = new DataTransfer();
    selected.forEach((file) => transfer.items.add(file));
    picker.files = transfer.files;
    previews.replaceChildren();
    selected.forEach((file, index) => {
      const card = document.createElement('div');
      card.className = 'photo-preview';
      const img = document.createElement('img');
      img.alt = `Preview of photo ${index + 1}`;
      const url = URL.createObjectURL(file);
      img.src = url;
      img.addEventListener('load', () => URL.revokeObjectURL(url), {once: true});
      const caption = document.createElement('span');
      caption.className = 'preview-caption';
      caption.textContent = file.name;
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = 'Remove';
      remove.setAttribute('aria-label', `Remove photo ${index + 1}: ${file.name}`);
      remove.addEventListener('click', () => {
        selected.splice(index, 1);
        showError('');
        render();
      });
      card.append(img, caption, remove);
      previews.append(card);
    });
  };
  const add = (files) => {
    if (selected.length + files.length > 3) {
      showError('Choose no more than three photos.');
      render();
      return;
    }
    selected.push(...files);
    showError('');
    render();
  };
  picker.addEventListener('change', () => add(Array.from(picker.files)));
  camera.addEventListener('change', () => {
    add(Array.from(camera.files));
    camera.value = '';
  });
}

const mainPhoto = document.querySelector('.gallery-main-image');
if (mainPhoto) {
  document.querySelectorAll('[data-gallery-thumb]').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      mainPhoto.src = thumb.dataset.photoSrc;
      mainPhoto.alt = thumb.dataset.photoAlt;
      document.querySelectorAll('[data-gallery-thumb]').forEach((button) => {
        const active = button === thumb;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-pressed', String(active));
      });
    });
  });
}
