/**
 * FAQ Announcements - Dynamic content from GitHub Issues
 *
 * Fetches and displays announcements from a GitHub repository's issues.
 * Supports three announcement types:
 * - Upcoming Changes (upcoming-change label)
 * - Known Issues (known-issue label)
 * - Recent Changes (recent-change label)
 *
 * Configuration is set via data attributes on the container elements
 * or via the global DEFINED in the Sphinx template.
 */

(function () {
  "use strict";

  // Configuration - can be overridden by setting window.FAQ_ANNOUNCEMENTS_CONFIG
  const DEFAULT_CONFIG = {
    // Repository to fetch from (owner/repo format)
    repo: "underwoo/rdhpcs-announcements-test",
    // Cache duration in milliseconds (5 minutes)
    cacheDuration: 5 * 60 * 1000,
    // Number of days to show time-based announcements
    displayDays: 60,
  };

  // Get configuration, allowing override from page
  const CONFIG = Object.assign(
    {},
    DEFAULT_CONFIG,
    window.FAQ_ANNOUNCEMENTS_CONFIG || {}
  );

  // API base URL
  const API_BASE = "https://api.github.com/repos";

  // Cache key prefix — increment version suffix to bust stale caches
  const CACHE_PREFIX = "faq_announcements_v2_";

  /**
   * Parse a date string in YYYY-MM-DD format or various other formats
   * @param {string} dateStr - Date string to parse
   * @returns {Date|null} - Parsed date or null if invalid
   */
  function parseDate(dateStr) {
    if (!dateStr) return null;

    // Try YYYY-MM-DD format first
    const isoMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (isoMatch) {
      return new Date(isoMatch[1], isoMatch[2] - 1, isoMatch[3]);
    }

    // Try natural date parsing as fallback
    const parsed = new Date(dateStr);
    return isNaN(parsed.getTime()) ? null : parsed;
  }

  /**
   * Check if a date is within the display window (past N days or future)
   * @param {Date} date - Date to check
   * @param {boolean} allowFuture - Whether to allow future dates
   * @returns {boolean} - True if date is within display window
   */
  function isWithinDisplayWindow(date, allowFuture = false) {
    if (!date) return true; // If no date, show it

    const now = new Date();
    const cutoffDate = new Date(now);
    cutoffDate.setDate(cutoffDate.getDate() - CONFIG.displayDays);

    if (allowFuture) {
      // For upcoming changes: show if date is in future or within past displayDays
      return date >= cutoffDate;
    } else {
      // For recent changes: show if date is within past displayDays
      return date >= cutoffDate && date <= now;
    }
  }

  /**
   * Parse the issue body to extract form fields
   * GitHub issue forms create a specific format in the body
   * @param {string} body - Issue body text
   * @returns {Object} - Parsed fields
   */
  function parseIssueBody(body) {
    const fields = {};
    if (!body) return fields;

    // GitHub issue forms create sections like:
    // ### Field Label
    //
    // Field value
    //
    // ### Next Field
    const sections = body.split(/^### /m);

    for (const section of sections) {
      if (!section.trim()) continue;

      const lines = section.split("\n");
      const label = lines[0].trim().toLowerCase().replace(/\s+/g, "-");
      const value = lines
        .slice(1)
        .join("\n")
        .trim()
        .replace(/^_No response_$/i, "");

      if (label && value) {
        fields[label] = value;
      }
    }

    return fields;
  }

  /**
   * Extract affected systems from checkbox responses
   * @param {Object} fields - Parsed fields
   * @returns {string[]} - Array of system names
   */
  function extractSystems(fields) {
    const systemsField = fields["affected-systems"] || "";
    const systems = [];

    // Checkboxes create lines like "- [X] System Name"
    const matches = systemsField.matchAll(/- \[X\] (.+)/gi);
    for (const match of matches) {
      systems.push(match[1].trim());
    }

    return systems;
  }

  /**
   * Extract severity from issue labels
   * @param {Object[]} labels - Issue labels array
   * @returns {string|null} - Severity level or null
   */
  function extractSeverity(labels) {
    for (const label of labels) {
      const match = label.name.match(/^severity:(.+)$/);
      if (match) {
        return match[1];
      }
    }
    return null;
  }

  /**
   * Fetch issues from GitHub API with caching
   * Requires both the specified label AND the "approved" label
   * @param {string} label - Label to filter by
   * @returns {Promise<Object[]>} - Array of issues
   */
  async function fetchIssues(label) {
    const cacheKey = CACHE_PREFIX + label;
    const cached = localStorage.getItem(cacheKey);

    if (cached) {
      try {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < CONFIG.cacheDuration) {
          return data;
        }
      } catch (e) {
        // Invalid cache, ignore
      }
    }

    // Require both the type label AND the approved label
    const labels = `${label},approved`;
    const url = `${API_BASE}/${CONFIG.repo}/issues?state=open&labels=${encodeURIComponent(labels)}&per_page=100`;

    const response = await fetch(url, {
      headers: {
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }

    const data = await response.json();

    // Cache the response
    localStorage.setItem(
      cacheKey,
      JSON.stringify({
        data: data,
        timestamp: Date.now(),
      })
    );

    return data;
  }

  /**
   * Create HTML for a severity badge
   * @param {string} severity - Severity level
   * @returns {string} - HTML string
   */
  function createSeverityBadge(severity) {
    if (!severity) return "";
    const severityClass = `faq-severity-${severity.toLowerCase()}`;
    return `<span class="faq-severity ${severityClass}">${severity}</span>`;
  }

  /**
   * Create HTML for system tags
   * @param {string[]} systems - Array of system names
   * @returns {string} - HTML string
   */
  function createSystemTags(systems) {
    if (!systems || systems.length === 0) return "";

    const tags = systems
      .map((s) => `<span class="faq-system-tag">${s}</span>`)
      .join("");

    return `<div class="faq-systems">Affects: ${tags}</div>`;
  }

  /**
   * Create HTML for a date display
   * @param {string} label - Label for the date
   * @param {string} dateStr - Date string
   * @returns {string} - HTML string
   */
  function createDateDisplay(label, dateStr) {
    if (!dateStr) return "";
    return `<div class="faq-date"><strong>${label}:</strong> ${dateStr}</div>`;
  }

  /**
   * Render an announcement as a dropdown
   * @param {Object} issue - GitHub issue object
   * @param {string} type - Announcement type
   * @returns {string} - HTML string
   */
  function renderAnnouncement(issue, type) {
    const fields = parseIssueBody(issue.body);
    const systems = extractSystems(fields);
    const severity = extractSeverity(issue.labels);

    // Get the title from the issue title (remove prefix like "[Known Issue] ")
    let title = issue.title.replace(/^\[(Known Issue|Recent Change|Upcoming)\]\s*/i, "");

    // Also check if there's a title field in the body
    const bodyTitle =
      fields["issue-title"] || fields["change-title"] || fields["title"];
    if (bodyTitle) {
      title = bodyTitle;
    }

    // Build the dropdown content
    let content = "";

    // Add severity badge for known issues
    if (type === "known-issue" && severity) {
      content += createSeverityBadge(severity);
    }

    // Add system tags
    content += createSystemTags(systems);

    // Add date information based on type
    if (type === "known-issue") {
      content += createDateDisplay("Identified", fields["date-identified"]);
      if (fields["expected-resolution"]) {
        content += createDateDisplay(
          "Expected Resolution",
          fields["expected-resolution"]
        );
      }
    } else {
      const dateField =
        fields["effective-date"] || fields["planned-effective-date"];
      const dateLabel =
        type === "upcoming-change" ? "Effective Date" : "Effective Date";
      content += createDateDisplay(dateLabel, dateField);
    }

    // Add description
    const description = fields["description"] || "";
    if (description) {
      content += `<div class="faq-description">${markdownToHtml(description)}</div>`;
    }

    // Add workaround for known issues
    if (type === "known-issue" && fields["workaround"]) {
      content += `<div class="faq-workaround"><strong>Workaround:</strong>${markdownToHtml(fields["workaround"])}</div>`;
    }

    // Add user action for changes
    if (
      (type === "recent-change" || type === "upcoming-change") &&
      fields["user-action-required"]
    ) {
      content += `<div class="faq-user-action"><strong>User Action Required:</strong>${markdownToHtml(fields["user-action-required"])}</div>`;
    }

    // Add documentation link
    const docLink = fields["documentation-link"] || fields["documentation"];
    if (docLink) {
      content += `<div class="faq-doc-link"><a href="${docLink}" target="_blank">More information</a></div>`;
    }

    // Add link to GitHub issue
    content += `<div class="faq-issue-link"><a href="${issue.html_url}" target="_blank">View on GitHub</a></div>`;

    // Create the dropdown HTML using sphinx-design structure
    return `
      <details class="sd-dropdown faq-item faq-dynamic-item">
        <summary class="sd-summary-title sd-card-header">
          ${title}
          <span class="sd-summary-icon sd-summary-down">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
              <path d="M12 16l-6-6h12z"/>
            </svg>
          </span>
          <span class="sd-summary-icon sd-summary-up">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
              <path d="M12 8l6 6H6z"/>
            </svg>
          </span>
        </summary>
        <div class="sd-summary-content sd-card-body">
          ${content}
        </div>
      </details>
    `;
  }

  /**
   * Simple markdown to HTML conversion for basic formatting
   * @param {string} text - Markdown text
   * @returns {string} - HTML string
   */
  function markdownToHtml(text) {
    if (!text) return "";

    return (
      text
        // Escape HTML
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        // Code blocks
        .replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>")
        // Inline code
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        // Bold
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        // Italic
        .replace(/\*([^*]+)\*/g, "<em>$1</em>")
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
        // Line breaks
        .replace(/\n/g, "<br>")
    );
  }

  /**
   * Render a section of announcements
   * @param {string} containerId - ID of the container element
   * @param {string} label - GitHub label to fetch
   * @param {string} type - Announcement type
   * @param {boolean} allowFuture - Whether to allow future dates
   */
  async function renderSection(containerId, label, type, allowFuture = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
      const issues = await fetchIssues(label);

      // Filter issues based on date
      const filteredIssues = issues.filter((issue) => {
        // Known issues don't have date filtering
        if (type === "known-issue") return true;

        const fields = parseIssueBody(issue.body);
        const dateStr =
          fields["effective-date"] || fields["planned-effective-date"];
        const date = parseDate(dateStr);

        return isWithinDisplayWindow(date, allowFuture);
      });

      if (filteredIssues.length === 0) {
        container.innerHTML = '<p class="faq-empty">There are no items in this section at this time.</p>';
        return;
      }

      // Render the announcements
      const html = filteredIssues
        .map((issue) => renderAnnouncement(issue, type))
        .join("");

      container.innerHTML = html;
    } catch (error) {
      console.error(`Error fetching ${type} announcements:`, error);

      // Show error message with link to GitHub
      const repoUrl = `https://github.com/${CONFIG.repo}/issues?q=label:${encodeURIComponent(label)}`;
      container.innerHTML = `
        <div class="faq-error">
          <p>Unable to load announcements. Please check
          <a href="${repoUrl}" target="_blank">GitHub Issues</a> directly.</p>
        </div>
      `;
    }
  }

  /**
   * Initialize all announcement sections
   */
  function init() {
    // Render each section
    renderSection(
      "faq-upcoming-changes",
      "upcoming-change",
      "upcoming-change",
      true
    );
    renderSection("faq-known-issues", "known-issue", "known-issue", false);
    renderSection("faq-recent-changes", "recent-change", "recent-change", false);
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
