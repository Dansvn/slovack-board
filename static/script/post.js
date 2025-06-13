function toggleComments() {
  const commentForm = document.getElementById('comment-form');
  const style = window.getComputedStyle(commentForm);
  if (style.display === 'none') {
    commentForm.style.display = 'block';
    commentForm.querySelector('input[name="comment"]').focus();
  } else {
    commentForm.style.display = 'none';
  }
}

async function toggleLike() {
  const likeBtn = document.getElementById('like-button');
  const likeImg = document.getElementById('like-img');
  const likeCount = document.getElementById('like-count');
  const postId = window.postData.id;

  const localKey = `liked_post_${postId}`;
  const alreadyLiked = localStorage.getItem(localKey) === 'true';

  // Só permite alternar curtida/unlike
  const action = alreadyLiked ? 'unlike' : 'like';

  try {
    const response = await fetch(`/post/${postId}/like`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action }),
    });

    const data = await response.json();

    if (!response.ok) throw new Error(data.error || 'Erro no like');

    likeCount.textContent = data.likes;

    const newLikedState = !alreadyLiked;
    likeImg.src = newLikedState ? window.postData.likedUrl : window.postData.likeUrl;

    if (newLikedState) {
      likeBtn.classList.add('liked');
      localStorage.setItem(localKey, 'true');
    } else {
      likeBtn.classList.remove('liked');
      localStorage.removeItem(localKey);
    }
  } catch {
    alert('Erro ao enviar like');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const postId = window.postData.id;
  const localKey = `liked_post_${postId}`;
  const liked = localStorage.getItem(localKey) === 'true';

  const likeBtn = document.getElementById('like-button');
  const likeImg = document.getElementById('like-img');

  if (liked) {
    likeImg.src = window.postData.likedUrl;
    likeBtn.classList.add('liked');
  } else {
    likeImg.src = window.postData.likeUrl;
    likeBtn.classList.remove('liked');
  }

  // Adiciona o evento no botão
  likeBtn.addEventListener('click', toggleLike);
});
