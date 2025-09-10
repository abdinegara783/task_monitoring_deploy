
;(() => {
  // CSRF Token helper
  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value
  }

  // API helper functions
  const api = {
    async post(url, data) {
      const formData = new FormData()
      Object.keys(data).forEach((key) => {
        if (Array.isArray(data[key])) {
          data[key].forEach((item, index) => {
            if (typeof item === "object") {
              Object.keys(item).forEach((subKey) => {
                formData.append(`${key}_${index}_${subKey}`, item[subKey])
              })
            } else {
              formData.append(`${key}_${index}`, item)
            }
          })
        } else {
          formData.append(key, data[key])
        }
      })
      formData.append("csrfmiddlewaretoken", getCSRFToken())

      const response = await fetch(url, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
      })
      return response.json()
    },

    async get(url, params = {}) {
      const urlParams = new URLSearchParams(params)
      const response = await fetch(`${url}?${urlParams}`)
      return response.json()
    },
  }

  // ROUTE DETECTION via template elements presence
  document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("btn-activity-report")) initForeman()
    if (document.querySelector(".view-reports-btn")) initEmployee()
    if (document.getElementById("btn-download-csv")) initAdmin()

    // Initialize common modals
    initCommonModals()
  })

  function initCommonModals() {
    // Profile Modal
    const profileBtn = document.getElementById("profile-btn")
    const profileModal = document.getElementById("modal-profile")
    if (profileBtn && profileModal) {
      profileBtn.addEventListener("click", () => profileModal.showModal())
      profileModal.addEventListener("click", (e) => {
        if (e.target.hasAttribute("data-close")) profileModal.close()
      })
    }

    // Settings Modal
    const settingsBtn = document.getElementById("settings-btn")
    const settingsModal = document.getElementById("modal-settings")
    if (settingsBtn && settingsModal) {
      settingsBtn.addEventListener("click", () => settingsModal.showModal())
      settingsModal.addEventListener("click", (e) => {
        if (e.target.hasAttribute("data-close")) settingsModal.close()
      })
    }
  }

  function initForeman() {
    // Elements
    const btnActivityReport = document.getElementById("btn-activity-report")
    const btnAnalysisReport = document.getElementById("btn-analysis-report")
    const modalActivity = document.getElementById("modal-activity")
    const modalAnalysis = document.getElementById("modal-analysis")
    const formActivity = document.getElementById("form-activity")
    const formAnalysis = document.getElementById("form-analysis")

    // Notification system
    initNotifications()

    // Activity Report Modal
    if (btnActivityReport && modalActivity) {
      btnActivityReport.addEventListener("click", () => {
        // Set today's date as default
        const dateInput = formActivity.querySelector('input[name="date"]')
        if (dateInput) {
          dateInput.value = new Date().toISOString().slice(0, 10)
        }
        modalActivity.showModal()
      })

      modalActivity.addEventListener("click", (e) => {
        if (e.target.hasAttribute("data-close")) modalActivity.close()
      })

      // Dynamic activities management
      initActivityManagement()
    }

    // Analysis Report Modal with Section Track
    if (btnAnalysisReport && modalAnalysis) {
      btnAnalysisReport.addEventListener("click", () => {
        showSectionTrackSelection()
        modalAnalysis.showModal()
      })

      modalAnalysis.addEventListener("click", (e) => {
        if (e.target.hasAttribute("data-close")) modalAnalysis.close()
      })

      // Section track selection
      initSectionTrackSelection()
    }

    // Form submissions
    if (formActivity) {
      formActivity.addEventListener("submit", handleActivitySubmit)
    }
    if (formAnalysis) {
      formAnalysis.addEventListener("submit", handleAnalysisSubmit)
    }
  }

  function initNotifications() {
    const notificationBtn = document.getElementById("notification-btn")
    const notificationDropdown = document.getElementById("notification-dropdown")

    if (notificationBtn && notificationDropdown) {
      notificationBtn.addEventListener("click", (e) => {
        e.stopPropagation()
        notificationDropdown.classList.toggle("hidden")
      })

      // Close dropdown when clicking outside
      document.addEventListener("click", () => {
        notificationDropdown.classList.add("hidden")
      })

      notificationDropdown.addEventListener("click", (e) => {
        e.stopPropagation()
      })
    }
  }

  function initActivityManagement() {
    const addActivityBtn = document.getElementById("add-activity")
    const activitiesSection = document.getElementById("activities-section")
    let activityCount = 1

    if (addActivityBtn) {
      addActivityBtn.addEventListener("click", () => {
        const activityHtml = `
          <div class="activity-item border rounded p-4 mb-4">
            <button type="button" class="remove-activity">×</button>
            <div class="form-field">
              <label class="label">Component *</label>
              <select name="component_${activityCount}" class="input" required>
                <option value="">Pilih Component</option>
                <option value="1000">1000: Engine</option>
                <option value="2000">2000: Clutch System</option>
                <option value="3000">3000: Transmission</option>
                <option value="4000">4000: Travel Drive-Axle</option>
                <option value="5000">5000: Steering</option>
                <option value="6000">6000: Undercarriage</option>
                <option value="7000">7000: Electric</option>
                <option value="8000">8000: Attachment</option>
                <option value="9000">9000: Periodical Service</option>
              </select>
            </div>
            <div class="form-field">
              <label class="label">Activities *</label>
              <textarea name="activities_${activityCount}" class="textarea" rows="3" required></textarea>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="form-field">
                <label class="label">SC</label>
                <input type="number" name="sc_${activityCount}" class="input" min="0" value="0">
              </div>
              <div class="form-field">
                <label class="label">USC</label>
                <input type="number" name="usc_${activityCount}" class="input" min="0" value="0">
              </div>
              <div class="form-field">
                <label class="label">ACD</label>
                <input type="number" name="acd_${activityCount}" class="input" min="0" value="0">
              </div>
            </div>
          </div>
        `

        addActivityBtn.insertAdjacentHTML("beforebegin", activityHtml)
        activityCount++
      })
    }

    // Remove activity handler
    activitiesSection.addEventListener("click", (e) => {
      if (e.target.classList.contains("remove-activity")) {
        e.target.closest(".activity-item").remove()
      }
    })
  }

  function initSectionTrackSelection() {
    const sectionTrackSelection = document.getElementById("section-track-selection")
    const analysisFormSection = document.getElementById("analysis-form-section")
    const backToSelectionBtn = document.getElementById("back-to-selection")
    const selectedTrackSpan = document.getElementById("selected-track")
    const sectionTrackInput = document.getElementById("section_track_input")

    // Section track buttons
    sectionTrackSelection.addEventListener("click", (e) => {
      const btn = e.target.closest(".section-track-btn")
      if (!btn) return

      const track = btn.getAttribute("data-track")
      selectedTrackSpan.textContent = track
      sectionTrackInput.value = track

      // Hide selection, show form
      sectionTrackSelection.classList.add("hidden")
      analysisFormSection.classList.remove("hidden")
    })

    // Back to selection
    if (backToSelectionBtn) {
      backToSelectionBtn.addEventListener("click", () => {
        showSectionTrackSelection()
      })
    }
  }

  function showSectionTrackSelection() {
    const sectionTrackSelection = document.getElementById("section-track-selection")
    const analysisFormSection = document.getElementById("analysis-form-section")

    sectionTrackSelection.classList.remove("hidden")
    analysisFormSection.classList.add("hidden")
  }

  async function handleActivitySubmit(e) {
    e.preventDefault()

    try {
      const formData = new FormData(e.target)
      const data = {}

      // Extract basic form data
      for (const [key, value] of formData.entries()) {
        data[key] = value
      }

      const response = await api.post("/api/reports/activity/", data)

      if (response.success) {
        document.getElementById("modal-activity").close()
        e.target.reset()
        showSuccessMessage("Laporan aktivitas berhasil disimpan")
        // Refresh page to show new report
        setTimeout(() => window.location.reload(), 1000)
      } else {
        showErrorMessage(response.error || "Gagal menyimpan laporan")
      }
    } catch (error) {
      console.error("Error submitting activity report:", error)
      showErrorMessage("Terjadi kesalahan saat menyimpan laporan")
    }
  }

  async function handleAnalysisSubmit(e) {
    e.preventDefault()

    try {
      const formData = new FormData(e.target)
      const data = {}

      for (const [key, value] of formData.entries()) {
        data[key] = value
      }

      const response = await api.post("/api/reports/analysis/", data)

      if (response.success) {
        document.getElementById("modal-analysis").close()
        e.target.reset()
        showSectionTrackSelection()
        showSuccessMessage("Laporan analisis berhasil disimpan")
        setTimeout(() => window.location.reload(), 1000)
      } else {
        showErrorMessage(response.error || "Gagal menyimpan laporan")
      }
    } catch (error) {
      console.error("Error submitting analysis report:", error)
      showErrorMessage("Terjadi kesalahan saat menyimpan laporan")
    }
  }

  function initEmployee() {
    const viewReportsBtns = document.querySelectorAll(".view-reports-btn")
    const reportsModal = document.getElementById("modal-reports")
    const validateModal = document.getElementById("modal-validate")
    const validateForm = document.getElementById("form-validate")

    // View reports buttons
    viewReportsBtns.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const foremanId = btn.getAttribute("data-foreman-id")
        const foremanName = btn.getAttribute("data-foreman-name")
        const reportType = btn.getAttribute("data-report-type")

        document.getElementById("modal-foreman-name").textContent = foremanName

        try {
          const response = await api.get("/api/reports/", {
            foreman_id: foremanId,
            type: reportType,
            status: "pending",
          })

          renderReportsTable(response.reports)
          reportsModal.showModal()
        } catch (error) {
          console.error("Error fetching reports:", error)
          showErrorMessage("Gagal memuat laporan")
        }
      })
    })

    // Close modals
    reportsModal.addEventListener("click", (e) => {
      if (e.target.hasAttribute("data-close")) reportsModal.close()
    })

    validateModal.addEventListener("click", (e) => {
      if (e.target.hasAttribute("data-close")) validateModal.close()
    })

    // Validate form submission
    if (validateForm) {
      validateForm.addEventListener("submit", handleValidateSubmit)
    }
  }

  function renderReportsTable(reports) {
    const tbody = document.getElementById("reports-table-body")

    tbody.innerHTML = reports
      .map(
        (report) => `
      <tr>
        <td>${report.date}</td>
        <td>${report.type === "activity" ? "Activity" : "Analysis"}</td>
        <td>${escapeHtml(report.title)}</td>
        <td>
          <span class="status-badge status-${report.status}">
            ${report.status_display}
          </span>
        </td>
        <td>
          <button class="btn btn-primary validate-btn" data-report-id="${report.id}">
            Validasi
          </button>
        </td>
      </tr>
    `,
      )
      .join("")

    // Add validate button handlers
    tbody.querySelectorAll(".validate-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const reportId = btn.getAttribute("data-report-id")
        await showValidateModal(reportId)
      })
    })
  }

  async function showValidateModal(reportId) {
    try {
      const response = await api.get(`/api/reports/${reportId}/`)

      document.getElementById("validate_report_id").value = reportId
      document.getElementById("report-summary").innerHTML = `
        <div class="p-3 rounded border">
          <div class="mb-1"><strong>${response.type === "activity" ? "Activity" : "Analysis"}</strong> · ${escapeHtml(response.title)}</div>
          <div class="text-sm text-gray-700">Tanggal: ${response.date} · Foreman: ${escapeHtml(response.foreman)}</div>
          <div class="text-sm mt-1">${escapeHtml(response.details.slice(0, 180))}${response.details.length > 180 ? "…" : ""}</div>
        </div>
      `

      document.getElementById("modal-validate").showModal()
    } catch (error) {
      console.error("Error fetching report details:", error)
      showErrorMessage("Gagal memuat detail laporan")
    }
  }

  async function handleValidateSubmit(e) {
    e.preventDefault()

    try {
      const formData = new FormData(e.target)
      const reportId = formData.get("report_id")
      const action = e.submitter.value // 'approve' or 'reject'
      const feedback = formData.get("feedback")

      const response = await api.post(`/api/reports/${reportId}/validate/`, {
        action: action,
        feedback: feedback,
      })

      if (response.success) {
        document.getElementById("modal-validate").close()
        document.getElementById("modal-reports").close()
        e.target.reset()
        showSuccessMessage(`Laporan berhasil ${action === "approve" ? "disetujui" : "ditolak"}`)
        setTimeout(() => window.location.reload(), 1000)
      } else {
        showErrorMessage(response.error || "Gagal memvalidasi laporan")
      }
    } catch (error) {
      console.error("Error validating report:", error)
      showErrorMessage("Terjadi kesalahan saat memvalidasi laporan")
    }
  }

  function initAdmin() {
    const btnDownloadCsv = document.getElementById("btn-download-csv")
    const btnClearData = document.getElementById("btn-clear-data")

    if (btnDownloadCsv) {
      btnDownloadCsv.addEventListener("click", () => {
        window.location.href = "/api/reports/export/csv/"
      })
    }

    if (btnClearData) {
      btnClearData.addEventListener("click", async () => {
        if (!confirm("Apakah Anda yakin ingin menghapus semua data laporan?")) return

        try {
          const response = await api.post("/api/reports/clear/", {})

          if (response.success) {
            showSuccessMessage("Semua data laporan berhasil dihapus")
            setTimeout(() => window.location.reload(), 1000)
          } else {
            showErrorMessage(response.error || "Gagal menghapus data")
          }
        } catch (error) {
          console.error("Error clearing data:", error)
          showErrorMessage("Terjadi kesalahan saat menghapus data")
        }
      })
    }
  }

  // Utility functions
  function escapeHtml(str) {
    const div = document.createElement("div")
    div.textContent = str
    return div.innerHTML
  }

  function showSuccessMessage(message) {
    // Create and show success toast/alert
    const alert = document.createElement("div")
    alert.className = "fixed top-4 right-4 bg-success-600 text-white p-4 rounded-lg shadow-lg z-50"
    alert.textContent = message
    document.body.appendChild(alert)

    setTimeout(() => {
      alert.remove()
    }, 3000)
  }

  function showErrorMessage(message) {
    // Create and show error toast/alert
    const alert = document.createElement("div")
    alert.className = "fixed top-4 right-4 bg-danger-600 text-white p-4 rounded-lg shadow-lg z-50"
    alert.textContent = message
    document.body.appendChild(alert)

    setTimeout(() => {
      alert.remove()
    }, 5000)
  }
})()