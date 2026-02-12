const menu= document.querySelector('#mobile-menu');
const menuLinks= document.querySelector('.navbar__menu');

menu.addEventListener('click', function() {
    menu.classList.toggle('is-active');
    menuLinks.classList.toggle('active');
});


function showForm(formId) {
    document.querySelectorAll(".form-box").forEach(form => form.classList.remove("active"));
    document.getElementById(formId).classList.add("active");
}

 const form1 = document.querySelector('form');
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            alert('Login successful!');
        });

function Cabinet() {}

const form = document.getElementById("complaintForm");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const image = document.getElementById("image").files[0];
  const location = document.getElementById("location").value;
  const description = document.getElementById("description").value;

  const formData = new FormData();
  formData.append("image", image);
  formData.append("location", location);
  formData.append("description", description);

  // POST to Django endpoint; include CSRF token
  const csrftoken = getCookie('csrftoken');
  try {
    const response = await fetch('/api/complaints/add/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    });
    const data = await response.json();
    if (data.success) {
      alert('Complaint submitted successfully!');
      form.reset();
      loadComplaints(); 
    } else {
      alert('Error: ' + (data.error || 'Failed to submit complaint'));
    }
  } catch (err) {
    console.error('Error submitting complaint:', err);
    alert('Error submitting complaint');
  }
});


async function loadComplaints() {
  const res = await fetch('/api/complaints/');
  const complaints = await res.json();

  const feed = document.getElementById("feed");
  feed.innerHTML = "";

  complaints.forEach(post => {
    feed.innerHTML += `
      <div class="post">
        ${post.image_url ? `<img src="${post.image_url}" alt="Complaint Image">` : ''}
        <div class="post-content">
          <h4>📍 ${post.location || ''}</h4>
          <p>${post.description || ''}</p>
          <p class="status">Status: ${post.resolved ? 'resolved' : 'open'}</p>
        </div>
      </div>
    `;
  });
}

function Sendissueactivate() {
    document.getElementById("complaintForm").style.display = "block";
    document.getElementById("feed").style.display = "none";
}

function Seeissuesactivate() {
    document.getElementById("complaintForm").style.display = "none";
    document.getElementById("feed").style.display = "block";
}

loadComplaints();

// Helper: get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
