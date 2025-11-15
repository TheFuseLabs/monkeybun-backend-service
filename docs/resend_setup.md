# Resend Email Setup Guide

This guide will help you set up Resend for sending transactional emails from `admin@monkeybun.fuselabs.com` using your domain `thefuselabs.com`.

## Prerequisites

- A Resend account (sign up at https://resend.com)
- Access to DNS settings for `thefuselabs.com` domain
- Admin access to your domain registrar or DNS provider

## Step 1: Create a Resend Account

1. Go to https://resend.com and sign up for an account
2. Verify your email address
3. Complete the onboarding process

## Step 2: Add Your Domain

1. Log in to your Resend dashboard
2. Navigate to **Domains** in the sidebar
3. Click **Add Domain**
4. Enter `fuselabs.com` (your root domain)
5. Click **Add Domain**

## Step 3: Configure DNS Records

Resend will provide you with DNS records that need to be added to your domain. You'll need to add these records to your DNS provider (e.g., Cloudflare, AWS Route 53, GoDaddy, etc.).

### Required DNS Records

Resend will show you the following records that need to be added:

1. **SPF Record** (TXT)
   - Name: `@` or `fuselabs.com`
   - Value: `v=spf1 include:resend.com ~all`

2. **DKIM Records** (TXT)
   - Resend will provide 3 DKIM records with specific names and values
   - These typically look like:
     - `resend._domainkey.fuselabs.com`
     - `resend1._domainkey.fuselabs.com`
     - `resend2._domainkey.fuselabs.com`

3. **DMARC Record** (TXT) - Optional but recommended
   - Name: `_dmarc.fuselabs.com`
   - Value: `v=DMARC1; p=none; rua=mailto:admin@fuselabs.com`

### Adding Records to Your DNS Provider

The exact steps depend on your DNS provider, but generally:

1. Log in to your DNS provider (where you manage DNS for `thefuselabs.com`)
2. Navigate to DNS management
3. Add each record provided by Resend
4. Save the changes

**Note:** DNS changes can take up to 48 hours to propagate, though they usually take effect within a few minutes to a few hours.

## Step 4: Verify Domain in Resend

1. Go back to the Resend dashboard
2. Navigate to **Domains**
3. Find `fuselabs.com` in your domain list
4. Click **Verify** - Resend will check if all DNS records are properly configured
5. Wait for verification to complete (this may take a few minutes to a few hours)

**Important:** The domain must show as "Verified" before you can send emails.

## Step 5: Set Up Subdomain (Optional but Recommended)

Since you want to send from `admin@monkeybun.fuselabs.com`, you have two options:

### Option A: Use the Root Domain (Simpler)

You can send from `admin@fuselabs.com` directly. The root domain will work once verified.

### Option B: Set Up Subdomain (Better for Organization)

If you want to use `monkeybun.fuselabs.com` as a subdomain:

1. In Resend, you can add `monkeybun.fuselabs.com` as a separate domain
2. Add the same DNS records but for the subdomain
3. Or, configure your DNS to allow the subdomain to inherit the root domain's email settings

**For most use cases, Option A is simpler and sufficient.** The email will come from `admin@monkeybun.fuselabs.com` but will use the root domain's verification.

## Step 6: Get Your API Key

1. In Resend dashboard, navigate to **API Keys**
2. Click **Create API Key**
3. Give it a name (e.g., "Monkeybun Backend Service")
4. Select the appropriate permissions (typically "Full Access" for production)
5. Click **Add**
6. **Copy the API key immediately** - you won't be able to see it again!

## Step 7: Configure Environment Variables

Add the following to your `.env` file:

```env
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=admin@monkeybun.fuselabs.com
RESEND_ENABLED=true
```

**Environment Variables:**
- `RESEND_API_KEY` (required): Your Resend API key
- `RESEND_FROM_EMAIL` (optional, default: `admin@monkeybun.fuselabs.com`): The email address to send from
- `RESEND_ENABLED` (optional, default: `true`): Set to `false` to disable email sending (useful for development/testing to avoid rate limits)

**To disable email sending during development:**
```env
RESEND_ENABLED=false
```

When disabled, emails will be logged but not actually sent, helping you avoid rate limits during testing.

**Important Security Notes:**
- Never commit your `.env` file to version control
- Keep your API key secure
- Rotate API keys periodically
- Use different API keys for development and production

## Step 8: Install Dependencies

The Resend dependency is already added to `pyproject.toml`. Install it:

```bash
uv sync
```

Or if using pip:

```bash
pip install resend>=3.0.0
```

## Step 9: Test Email Sending

You can test the email setup by:

1. Starting your application
2. Creating a test application through the API
3. Checking that emails are sent to the configured recipients

Check the Resend dashboard under **Logs** to see email delivery status.

## Troubleshooting

### Domain Not Verifying

- **Check DNS propagation:** Use tools like `dig` or online DNS checkers to verify records are propagated
- **Wait longer:** DNS changes can take up to 48 hours
- **Double-check records:** Ensure all records match exactly what Resend provided
- **Check for typos:** Verify domain names and record values are correct

### Emails Not Sending

- **Verify domain status:** Ensure domain shows as "Verified" in Resend
- **Check API key:** Verify `RESEND_API_KEY` is set correctly in your `.env`
- **Check logs:** Look at application logs for error messages
- **Check Resend logs:** Check the Resend dashboard for delivery status
- **Verify recipient emails:** Ensure recipient email addresses are valid

### Emails Going to Spam

- **Set up DMARC:** Add the DMARC record mentioned in Step 3
- **Warm up domain:** Start with low email volumes and gradually increase
- **Use proper email content:** Avoid spam trigger words
- **Monitor reputation:** Check Resend dashboard for reputation metrics

### Subdomain Issues

If you're having issues with `monkeybun.fuselabs.com`:

- Try using `admin@fuselabs.com` instead
- Or add `monkeybun.fuselabs.com` as a separate domain in Resend
- Ensure DNS records are configured for the subdomain

## Email Templates

The application automatically sends emails for:

1. **Application Created** - Sent to market organizer when a new application is submitted
2. **Application Accepted** - Sent to business owner when their application is accepted
3. **Application Rejected** - Sent to business owner when their application is declined (includes rejection reason)
4. **Payment Updated** - Sent to both business owner and market organizer when payment info is updated
5. **Application Confirmed** - Sent to both business owner and market organizer when application is confirmed

All email templates are defined in `src/module/application/service/email_service.py` and can be customized as needed.

## Production Considerations

1. **Rate Limits:** Resend has rate limits based on your plan. Monitor usage in the dashboard
2. **Monitoring:** Set up alerts for failed email deliveries
3. **Error Handling:** The application logs email errors but doesn't fail the request if email sending fails
4. **Email Validation:** Ensure email addresses in your database are valid before sending
5. **Unsubscribe:** For marketing emails, implement unsubscribe functionality (not needed for transactional emails)

## Support

- Resend Documentation: https://resend.com/docs
- Resend Support: support@resend.com
- Check application logs for detailed error messages

