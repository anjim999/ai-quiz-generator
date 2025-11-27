import { BREVO_API_KEY, EMAIL_FROM } from '../config/env.js';
async function sendOtpEmail({ to, otp, purpose }) {
  try {
    const subject =
      purpose === 'REGISTER'
        ? 'Your Registration OTP - Inventory App'
        : 'Your Password Reset OTP - Inventory App';

    const htmlContent = `
      <div style="font-family: Arial; font-size:14px; color:#333;">
        <p><strong>Your OTP:</strong></p>
        <h2 style="letter-spacing:4px">${otp}</h2>
        <p>This OTP is valid for 10 minutes.</p>
      </div>
    `;

    const [senderName, senderEmailRaw] = EMAIL_FROM.includes('<')
      ? EMAIL_FROM.split('<')
      : [null, EMAIL_FROM];

    const sender = {
      email: senderEmailRaw.replace('>', '').trim(),
      ...(senderName ? { name: senderName.trim() } : {}),
    };

    const body = {
      sender,
      to: [{ email: to }],
      subject,
      htmlContent,
    };

    const res = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-key': BREVO_API_KEY,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      console.error('Brevo API error:', res.status, text);
      return { success: false, error: new Error(`Brevo API ${res.status}`) };
    }

    const data = await res.json();
    console.log('OTP Email sent via Brevo API:', data.messageId || data);

    return { success: true };
  } catch (error) {
    console.error('Error sending Brevo email via API:', error);
    return { success: false, error };
  }
}

export { sendOtpEmail };