// Contact form component — self-contained, powered by Web3Forms (https://web3forms.com).
// To remove this form: delete the <div id="contact-form-root"></div> placeholder and the
// <script src="contact-form.js"> tag from index.html. Nothing else depends on this file.
(function () {
  const WEB3FORMS_ACCESS_KEY = "64f5b5ea-04fa-4444-8486-05b3fc29435f"; // get one free at https://web3forms.com

  const root = document.getElementById("contact-form-root");
  if (!root) return;

  root.innerHTML = `
    <section class="py-5 bg-light" id="contact">
      <div class="container" style="max-width:420px;">
        <h2 class="fw-bold text-center">Request a Free Quote</h2>
        <div class="accent-bar mx-auto mb-4"></div>

        <div id="qfFormWrap">
          <form id="quoteForm" novalidate>
            <input type="hidden" name="access_key" value="${WEB3FORMS_ACCESS_KEY}">
            <input type="hidden" name="subject" value="New Quote Request - Lifetime Garage Flooring">
            <input type="checkbox" name="botcheck" class="d-none" style="display:none" tabindex="-1" autocomplete="off">

            <div id="qfStep1">
              <p class="text-muted small mb-3">We offer free estimates on residential garage flooing. Fill out the form below to request your complimentary consultation. </p>
              <div class="row mb-3 align-items-center">
                <label for="qfName" class="col-4 col-form-label">Name</label>
                <div class="col-8">
                  <input type="text" class="form-control" id="qfName" name="name" required>
                </div>
              </div>

              <div class="row mb-3 align-items-center">
                <label for="qfEmail" class="col-4 col-form-label">Email</label>
                <div class="col-8">
                  <input type="email" class="form-control" id="qfEmail" name="email" required>
                </div>
              </div>

              <div class="row mb-3 align-items-center">
                <label for="qfPhone" class="col-4 col-form-label">Phone</label>
                <div class="col-8">
                  <input type="tel" class="form-control" id="qfPhone" name="phone">
                </div>
              </div>

              <button type="button" class="btn btn-primary btn-lg w-100" id="qfNext">Submit</button>
            </div>

            <div id="qfStep2" class="d-none">
              <p class="text-muted small mb-3">One more thing...</p>

              <div class="row mb-3">
                <label for="qfMessage" class="col-4 col-form-label">Tell us about your garage</label>
                <div class="col-8">
                  <textarea class="form-control" id="qfMessage" name="message" rows="4" required></textarea>
                </div>
              </div>

              <div id="qfStatus" role="status" aria-live="polite" class="mb-3"></div>

              <div class="d-flex gap-2">
                <button type="button" class="btn btn-outline-secondary" id="qfBack">Back</button>
                <button type="submit" class="btn btn-primary btn-lg flex-grow-1" id="qfSubmit">Send Request</button>
              </div>
            </div>
          </form>

          <p class="text-muted small text-center mt-3 mb-0">
            <i class="bi bi-shield-lock-fill me-1"></i>
            Your privacy matters to us. Information submitted here is used solely to respond to your quote request and is never sold or shared with third parties.
          </p>
        </div>

        <div id="qfThankYou" class="d-none text-center py-4" role="status" aria-live="polite">
          <i class="bi bi-check-circle-fill text-primary fs-1 mb-3 d-block"></i>
          <h3 class="h4 fw-bold mb-2">Thank you!</h3>
          <p class="text-muted mb-0">We got your request and will be in touch shortly. <br>If it's urgent, call us at
            <a href="tel:+18132134050" class="link-primary text-decoration-none">(813) 213-4050</a>.</p>
        </div>
      </div>
    </section>
  `;

  const form = document.getElementById("quoteForm");
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
    if (!WEB3FORMS_ACCESS_KEY || WEB3FORMS_ACCESS_KEY === "YOUR_ACCESS_KEY_HERE") return;
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

    if (!WEB3FORMS_ACCESS_KEY || WEB3FORMS_ACCESS_KEY === "YOUR_ACCESS_KEY_HERE") {
      statusEl.innerHTML =
        '<div class="alert alert-warning mb-0">Form isn\'t configured yet — add your Web3Forms access key in contact-form.js.</div>';
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
