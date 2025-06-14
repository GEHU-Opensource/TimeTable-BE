const API_BASE = "http://127.0.0.1:8000/api";
const token = localStorage.getItem("access_token");

export function authFetch(endpoint, options = {}) {
  options.headers = {
    ...(options.headers || {}),
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };
  return fetch(API_BASE + endpoint, options)
    .then(res => {
      if (!res.ok) throw res;
      return res.json();
    });
}

export function showLoader() {
  document.getElementById("loader").style.display = "block";
}

export function hideLoader() {
  document.getElementById("loader").style.display = "none";
}