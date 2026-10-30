// Run in the open detail page with Playwright's page.evaluate().
// This only reads visible table fields. Navigation happens in capture_tenders.py.
(arg) => {
  const wanted = new Set([
    "Organisation Chain", "Tender Reference Number", "Tender ID", "Withdrawal Allowed",
    "Tender Type", "Form Of Contract", "Tender Category", "No. of Covers",
    "Payment Mode", "Tender Fee in ₹", "Processing Fee in ₹", "EMD Amount in ₹",
    "EMD Exemption Allowed", "Title", "Work Description", "NDA/Pre Qualification",
    "Tender Value in ₹", "Product Category", "Sub category", "Contract Type",
    "Bid Validity(Days)", "Period Of Work(Days)", "Location", "Pincode",
    "Tenderer Class", "Published Date", "Bid Opening Date",
    "Bid Submission Start Date", "Bid Submission End Date",
  ]);
  const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const fields = {};

  // A row can contain one, two, or three label/value pairs. Skip wrapper rows
  // with nested tables so a section heading cannot overwrite a real field.
  for (const row of document.querySelectorAll("tr")) {
    const cells = Array.from(row.cells || []);
    if (cells.length < 2 || cells.length % 2 || cells.some(cell => cell.querySelector("table"))) continue;
    for (let i = 0; i < cells.length; i += 2) {
      const label = clean(cells[i].innerText);
      if (wanted.has(label)) fields[label] = clean(cells[i + 1].innerText);
    }
  }

  // Document download URLs depend on the portal session. We retain names and
  // whether a link was displayed; we do not present the URL as a stable link.
  const documents = [];
  for (const [selector, kind, nameColumn] of [
    ["table#table", "NIT", 1],
    ["table#workItemDocumenttable", "work item", 2],
  ]) {
    const table = document.querySelector(selector);
    if (!table) continue;
    for (const row of Array.from(table.rows).slice(1)) {
      const cells = Array.from(row.cells);
      if (cells.length <= nameColumn) continue;
      const name = clean(cells[nameColumn].innerText);
      if (!name) continue;
      const link = cells[nameColumn].querySelector("a[href]");
      documents.push({ kind, name, link_present: !!link });
    }
  }
  const required = ["Tender ID", "Title", "Published Date"];
  const missing_required = required.filter(key => !fields[key]);
  // A search form may show a challenge. The caller stops when this is reported.
  const captchaVisible = /\bcaptcha\b/i.test(document.body.innerText) ||
    !!document.querySelector('input[id*="captcha" i], input[name*="captcha" i]');
  const status = captchaVisible ? "captcha" : missing_required.length === 0 ? "captured" : "unavailable";
  return {
    url: arg.url,
    resolved_url: location.href,
    categories: arg.categories || [],
    captured_at_utc: new Date().toISOString(),
    status,
    fields,
    documents,
    missing_required,
  };
}
