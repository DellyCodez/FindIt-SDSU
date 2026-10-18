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

const photoInput = document.querySelector('#photos');
const cameraInput = document.querySelector('#photo-camera');
const dropzone = document.querySelector('#photo-dropzone');
const previews = document.querySelector('#photo-previews');
const feedback = document.querySelector('#photo-feedback');
if (photoInput && cameraInput && dropzone && previews && feedback && window.DataTransfer) {
  let selected = [];
  const allowed = new Set(['image/jpeg', 'image/png', 'image/webp']);
  function renderPhotos() {
    const transfer = new DataTransfer();
    selected.forEach(({ file }) => transfer.items.add(file));
    photoInput.files = transfer.files;
    previews.replaceChildren();
    selected.forEach(({ file, url }, index) => {
      const card = document.createElement('div');
      card.className = 'photo-preview';
      const image = document.createElement('img');
      image.src = url;
      image.alt = `Preview ${index + 1}: ${file.name}`;
      const name = document.createElement('span');
      name.textContent = file.name;
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = 'Remove';
      remove.setAttribute('aria-label', `Remove photo ${index + 1}: ${file.name}`);
      remove.addEventListener('click', () => {
        URL.revokeObjectURL(url);
        selected.splice(index, 1);
        renderPhotos();
      });
      card.append(image, name, remove);
      previews.append(card);
    });
    feedback.textContent = selected.length ? `${selected.length} of 3 photos selected.` : 'No photos selected.';
  }
  function addPhotos(files) {
    const incoming = Array.from(files);
    if (incoming.length + selected.length > 3) {
      renderPhotos();
      feedback.textContent = 'Choose no more than three photos.';
      return;
    }
    if (incoming.some(file => !allowed.has(file.type) || file.size > 8 * 1024 * 1024)) {
      renderPhotos();
      feedback.textContent = 'Choose JPEG, PNG, or WebP files, each 8 MB or smaller.';
      return;
    }
    selected.push(...incoming.map(file => ({ file, url: URL.createObjectURL(file) })));
    renderPhotos();
  }
  photoInput.addEventListener('change', () => addPhotos(photoInput.files));
  cameraInput.addEventListener('change', () => {
    addPhotos(cameraInput.files);
    cameraInput.value = '';
  });
  ['dragenter', 'dragover'].forEach(eventName => dropzone.addEventListener(eventName, event => {
    event.preventDefault();
    dropzone.classList.add('is-dragging');
  }));
  ['dragleave', 'drop'].forEach(eventName => dropzone.addEventListener(eventName, event => {
    event.preventDefault();
    dropzone.classList.remove('is-dragging');
  }));
  dropzone.addEventListener('drop', event => addPhotos(event.dataTransfer.files));
}

const galleryMain = document.querySelector('#gallery-main');
const galleryCaption = document.querySelector('#gallery-caption');
const galleryButtons = document.querySelectorAll('.gallery-thumb');
if (galleryMain && galleryCaption && galleryButtons.length) {
  galleryButtons.forEach(button => button.addEventListener('click', () => {
    galleryMain.src = button.dataset.photoUrl;
    galleryMain.alt = `Photo ${button.dataset.photoNumber} of ${galleryButtons.length} showing this item`;
    galleryCaption.textContent = `Photo ${button.dataset.photoNumber} of ${galleryButtons.length} · uploaded with this fictional report`;
    galleryButtons.forEach(other => {
      other.classList.toggle('is-active', other === button);
      other.setAttribute('aria-pressed', String(other === button));
    });
  }));
}
