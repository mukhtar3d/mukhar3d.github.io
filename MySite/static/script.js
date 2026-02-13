const menu = document.querySelector("#mobile-menu");
const menuLinks = document.querySelector(".navbar__menu");

console.log("[script.js] Script loaded!");

if (menu && menuLinks) {
  menu.addEventListener("click", function () {
    menu.classList.toggle("is-active");
    menuLinks.classList.toggle("active");
  });
}

function showForm(formId) {
  document
    .querySelectorAll(".form-box")
    .forEach((form) => form.classList.remove("active"));
  document.getElementById(formId).classList.add("active");
}

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
  const csrftoken = getCookie("csrftoken");
  try {
    const response = await fetch("/api/complaints/add/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      body: formData,
    });
    const data = await response.json();
    if (data.success) {
      alert("Complaint submitted successfully!");
      form.reset();
      loadComplaints();
    } else {
      alert("Error: " + (data.error || "Failed to submit complaint"));
    }
  } catch (err) {
    console.error("Error submitting complaint:", err);
    alert("Error submitting complaint");
  }
});

async function loadComplaints() {
  try {
    const feed = document.getElementById("feed");
    if (!feed) {
      console.error("Feed element not found!");
      return;
    }

    feed.innerHTML = "<p>Loading complaints...</p>";
    console.log("Fetching complaints from /api/complaints/");

    const res = await fetch("/api/complaints/");
    console.log("Response status:", res.status);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const complaints = await res.json();
    console.log("Complaints received:", complaints);

    feed.innerHTML = "";

    if (!complaints || complaints.length === 0) {
      console.log("No complaints found");
      feed.innerHTML = "<p>No complaints found.</p>";
      return;
    }

    console.log(`Rendering ${complaints.length} complaints`);
    complaints.forEach((post) => {
      const date = post.created_at
        ? new Date(post.created_at).toLocaleDateString()
        : "Unknown";
      feed.innerHTML += `
        <div class="post" style="border: 1px solid #dbdbdb; padding: 10px; margin: 20px 0;" border-radius: 10px; background-color: #75a4c4;">
          ${post.image_url ? `<img src="${post.image_url}" alt="Complaint Image" style="max-width: 200px;">` : ""}
          <div class="post-content">
            <h4 style="color: #000000"> ${post.location || "No location"}</h4>
            <p style="color: #000000">${post.description || ""}</p>
            <p style="color: #000000"><strong>Severity:</strong> ${post.severity || "low"}</p>
            <p class="status" style="color: #000000; font-size: 1rem;"><strong>Status:</strong> ${post.status || "pending"}</p>
            <p style="font-size: 1rem; color: #000000;">Reported by: ${post.user_id || "Anonymous"} on ${date}</p>
          </div>
        </div>
      `;
    });
  } catch (err) {
    console.error("Error loading complaints:", err);
    const feed = document.getElementById("feed");
    if (feed) {
      feed.innerHTML =
        "<p style='color: red;'>Error loading complaints: " +
        (err.message || err) +
        "</p>";
    }
  }
}

function Sendissueactivate() {
  document.getElementById("complaintFormContainer").style.display = "block";
  document.getElementById("feed").style.display = "none";
}

function Seeissuesactivate() {
  document.getElementById("complaintFormContainer").style.display = "none";
  document.getElementById("feed").style.display = "block";
  loadComplaints();
}

// Initialize when DOM is ready or immediately if already loaded
function initializePage() {
  console.log("Initializing page!");
  console.log("Feed element exists:", !!document.getElementById("feed"));
  loadComplaints();
}

// Try to load immediately if DOM is ready
if (document.readyState === "loading") {
  console.log("DOM still loading, waiting for DOMContentLoaded");
  document.addEventListener("DOMContentLoaded", initializePage);
} else {
  console.log("DOM already loaded, initializing immediately");
  initializePage();
}

// Helper: get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
