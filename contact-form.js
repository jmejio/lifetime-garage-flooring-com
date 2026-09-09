// Contact form behavior — powered by Web3Forms (https://web3forms.com).
// The form's markup is server-rendered by components.contact_form() in
// build/templates/_components.jinja (build/build.py provides the access key as
// the "web3forms_access_key" template global); this file only wires up the
// two-step navigation and the submit/fetch logic on whatever a page already
// rendered. Pages that don't include the form (e.g. the /locations/,
// /resources/, /projects/ index pages) simply have no #quoteForm, so this
// script no-ops on them.
(function () {
  const form = document.getElementById("quoteForm");
  if (!form) return;

  const accessKey = form.access_key.value;
  const statusEl = document.getElementById("qfStatus");
  const submitBtn = document.getElementById("qfSubmit");
  const formWrap = document.getElementById("qfFormWrap");
  const thankYou = document.getElementById("qfThankYou");
  const step1 = document.getElementById("qfStep1");
  const step2 = document.getElementById("qfStep2");
  const nextBtn = document.getElementById("qfNext");
  const backBtn = document.getElementById("qfBack");
  const nameInput = document.getElementById("qfName");
  const emailInput = document.getElementById("qfEmail");
  const messageInput = document.getElementById("qfMessage");

  // Capture Step 1 in the background as soon as the visitor moves on, so their
  // contact info isn't lost if they never finish Step 2. Fires at most once.
  let step1Captured = false;
  function captureStep1() {
    if (step1Captured) return;
    if (!accessKey || accessKey === "YOUR_ACCESS_KEY_HERE") return;
    step1Captured = true;

    const payload = Object.fromEntries(new FormData(form));
    payload.subject = "Partial Quote Request (Step 1 only) - Lifetime Garage Flooring";
    payload.message = "(Visitor provided contact info but has not described their project yet.)";

    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    }).catch(function () {
      // Non-blocking: if this fails, the visitor can still complete Step 2 normally.
    });
  }

  nextBtn.addEventListener("click", function () {
    if (!nameInput.checkValidity()) {
      nameInput.reportValidity();
      return;
    }
    if (!emailInput.checkValidity()) {
      emailInput.reportValidity();
      return;
    }
    captureStep1();
    step1.classList.add("d-none");
    step2.classList.remove("d-none");
    messageInput.focus();
  });

  backBtn.addEventListener("click", function () {
    step2.classList.add("d-none");
    step1.classList.remove("d-none");
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    if (!accessKey || accessKey === "YOUR_ACCESS_KEY_HERE") {
      statusEl.innerHTML =
        '<div class="alert alert-warning mb-0">Form isn\'t configured yet — set web3forms_access_key in build/build.py.</div>';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Sending...";
    statusEl.innerHTML = "";

    try {
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      const result = await res.json();

      if (result.success) {
        form.reset();
        formWrap.classList.add("d-none");
        thankYou.classList.remove("d-none");
      } else {
        throw new Error(result.message || "Submission failed");
      }
    } catch (err) {
      statusEl.innerHTML =
        '<div class="alert alert-danger mb-0">Something went wrong. Please call us at (813) 213-4050 instead.</div>';
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Send Request";
    }
  });
})();
