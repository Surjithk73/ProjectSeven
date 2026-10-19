export async function accountOverview() {
  return fetch('/api/banking/accounts');
}
export async function sendMoney(source, destination, amount_cents) {
  return fetch('/api/banking/transfer', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({source, destination, amount_cents})});
}
export async function reverseTransfer(transaction_id) {
  return fetch('/api/banking/refund', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({transaction_id})});
}
export async function transactionHistory() {
  return fetch('/api/banking/transactions');
}
export async function savedRecipients() {
  return fetch('/api/banking/beneficiaries');
}
