import Link from 'next/link';
import type { Metadata } from 'next';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { LegalSection } from '@/components/ui/legal-section';

export const metadata: Metadata = {
  title: 'Privacy Policy | ToxShield',
  description:
    'ToxShield Privacy Policy — how we collect, use, and protect your data.',
};

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen flex flex-col bg-surface-0/50 relative overflow-hidden">
      <AuroraBackground seed={333} />

      {/* Terminal header bar */}
      <div className="relative z-10 flex items-center gap-2 px-4 py-2 arcane-glass border-b border-neon-cyan/[0.08] font-mono text-xs pt-safe">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-neon-magenta/60" />
          <span className="w-2 h-2 rounded-full bg-warning-amber/60" />
          <span className="w-2 h-2 rounded-full bg-neon-mint/60" />
        </div>
        <div className="flex-1 text-center text-text-secondary">
          toxshield://privacy
        </div>
      </div>

      <main className="relative z-10 flex-1 px-4 py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Back link */}
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 font-mono text-xs text-neon-cyan/60 active:text-neon-cyan transition-colors min-h-[44px]"
          >
            &larr; Back
          </Link>

          {/* Header */}
          <div className="arcane-glass-intense p-6 sm:p-8 space-y-2">
            <p className="font-mono text-[10px] text-neon-magenta tracking-[0.3em] uppercase">
              // legal_document
            </p>
            <h1 className="text-2xl sm:text-3xl font-bold font-display text-text-primary tracking-[0.1em] text-glow">
              PRIVACY POLICY
            </h1>
            <p className="font-mono text-xs text-text-secondary">
              Last updated: March 30, 2026
            </p>
          </div>

          {/* Content */}
          <div className="arcane-glass-intense p-6 sm:p-8 space-y-8">
            <LegalSection id="introduction" title="1. Introduction">
              <p>
                ToxShield (&ldquo;we,&rdquo; &ldquo;our,&rdquo; or &ldquo;us&rdquo;) operates the website at{' '}
                <Link href="https://toxshield.in" className="text-neon-cyan underline underline-offset-2">
                  toxshield.in
                </Link>{' '}
                and the ToxShield mobile application (collectively, the &ldquo;Service&rdquo;). This Privacy
                Policy explains how we collect, use, disclose, and safeguard your information when you use
                our Service.
              </p>
              <p>
                By using ToxShield, you agree to the collection and use of information in accordance with
                this policy. If you do not agree, please do not use the Service.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="information-we-collect" title="2. Information We Collect">
              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider">
                2.1 Account Information
              </p>
              <p>
                When you create an account, we collect your email address, display name, and (if you sign
                up via Google OAuth) your Google profile avatar URL. This information is required to provide
                you access to the Service.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.2 User-Generated Content
              </p>
              <p>
                You may submit behavioral descriptions (free-form text), WhatsApp chat exports, and Slack
                chat exports for AI analysis. This content is stored in our database linked to your account
                and the person you are analyzing.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.3 AI-Generated Analysis Results
              </p>
              <p>
                When you submit content for analysis, our AI generates: toxicity scores (0&ndash;10), risk
                levels, detected behavioral traits, pattern analysis summaries, protection strategies,
                self-reflection feedback, threat type classifications, headlines, taglines, and user
                insights (analysis of your own communication patterns). These results are stored in our
                database associated with your account.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.4 People Directory
              </p>
              <p>
                You may create entries for people you wish to analyze, including their name and your
                relationship to them (e.g., ex-partner, boss, friend). Toxicity scores and risk levels
                are associated with each person entry.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.5 Mood &amp; Wellness Data
              </p>
              <p>
                You may optionally record daily mood check-ins consisting of a mood score (1&ndash;5) and
                an optional note (up to 200 characters). This data is used for the wellness tracking
                feature and is not shared with third parties.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.6 Purchase Information
              </p>
              <p>
                When you purchase an analysis pack, we store the pack type, purchase status, payment
                gateway used (Stripe or Razorpay), and the corresponding payment session/order IDs. We
                do <strong className="text-neon-mint">not</strong> store your credit card number, CVV, or
                full payment card details &mdash; these are handled entirely by our payment processors.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.7 Gamification Data
              </p>
              <p>
                We automatically track your usage streaks (consecutive days of activity), earned badges,
                and monthly analysis usage counts to power the gamification features of the Service.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.8 Referral Data
              </p>
              <p>
                If you participate in our referral program, we store your unique referral code and track
                referral relationships (who referred whom) and referral status.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.9 Push Notification Data
              </p>
              <p>
                If you opt in to push notifications, we store your Web Push subscription endpoint and
                encryption keys to deliver notifications to your device.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                2.10 Analytics
              </p>
              <p>
                We use Vercel Analytics to collect anonymized, aggregate page view and performance data.
                This data contains no personally identifiable information and uses cookieless tracking.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="how-we-use" title="3. How We Use Your Information">
              <ul className="list-disc list-inside space-y-1.5 text-text-secondary">
                <li>To provide AI-powered behavioral analysis (core service functionality)</li>
                <li>To maintain your people directory and analysis history</li>
                <li>To process payments for analysis packs via Stripe or Razorpay</li>
                <li>To track streaks, badges, and gamification features</li>
                <li>To send push notifications when you have opted in</li>
                <li>To manage the referral program</li>
                <li>To improve the Service through anonymized analytics</li>
                <li>To communicate service updates or policy changes</li>
              </ul>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="ai-processing" title="4. AI Processing Disclosure">
              <p>
                ToxShield uses the Anthropic Claude API to analyze behavioral descriptions and chat
                content you submit. When you request an analysis, the text content you provide (along
                with the person&apos;s name and relationship type) is sent to Anthropic&apos;s servers for
                processing.
              </p>
              <p>
                Anthropic&apos;s API data policy states that API inputs are{' '}
                <strong className="text-neon-mint">not used for model training</strong> by default. For
                more information, see{' '}
                <Link
                  href="https://www.anthropic.com/policies"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-neon-cyan underline underline-offset-2"
                >
                  Anthropic&apos;s usage policies
                </Link>
                .
              </p>
              <p className="arcane-glass p-3 text-xs text-warning-amber">
                <strong>Important:</strong> AI-generated analysis results are algorithmic assessments
                based on the text you provide. They are not clinical diagnoses and should not be treated
                as substitutes for professional mental health counseling, therapy, or diagnosis.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="third-party-services" title="5. Third-Party Services">
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-mono">
                  <thead>
                    <tr className="border-b border-neon-cyan/[0.08]">
                      <th className="text-left py-2 text-neon-cyan/70 uppercase tracking-wider">Service</th>
                      <th className="text-left py-2 text-neon-cyan/70 uppercase tracking-wider">Data Shared</th>
                      <th className="text-left py-2 text-neon-cyan/70 uppercase tracking-wider">Purpose</th>
                    </tr>
                  </thead>
                  <tbody className="text-text-secondary">
                    <tr className="border-b border-neon-cyan/[0.04]">
                      <td className="py-2 text-text-primary">Anthropic (Claude API)</td>
                      <td className="py-2">Behavioral descriptions, chat content</td>
                      <td className="py-2">AI analysis</td>
                    </tr>
                    <tr className="border-b border-neon-cyan/[0.04]">
                      <td className="py-2 text-text-primary">Stripe</td>
                      <td className="py-2">Email, purchase metadata</td>
                      <td className="py-2">Payment processing (international)</td>
                    </tr>
                    <tr className="border-b border-neon-cyan/[0.04]">
                      <td className="py-2 text-text-primary">Razorpay</td>
                      <td className="py-2">Email, purchase metadata</td>
                      <td className="py-2">Payment processing (India)</td>
                    </tr>
                    <tr className="border-b border-neon-cyan/[0.04]">
                      <td className="py-2 text-text-primary">Supabase</td>
                      <td className="py-2">All user data (hosted database)</td>
                      <td className="py-2">Database &amp; authentication</td>
                    </tr>
                    <tr className="border-b border-neon-cyan/[0.04]">
                      <td className="py-2 text-text-primary">Google (OAuth)</td>
                      <td className="py-2">Email, name, avatar (received)</td>
                      <td className="py-2">Social login</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-text-primary">Vercel Analytics</td>
                      <td className="py-2">Anonymized page views (no PII)</td>
                      <td className="py-2">Usage analytics</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p className="pt-2">
                We do <strong className="text-neon-mint">not</strong> sell your personal data to third
                parties. Data is shared only with the service providers listed above, solely for the
                purposes described.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="data-storage" title="6. Data Storage &amp; Retention">
              <p>
                Your data is stored in Supabase-managed PostgreSQL databases with cloud infrastructure
                encryption. Data is retained as follows:
              </p>
              <ul className="list-disc list-inside space-y-1.5">
                <li>Account and analysis data: retained until you request account deletion</li>
                <li>People and their analyses: retained until you delete the person or your account</li>
                <li>Purchase records: retained for legal and financial compliance requirements</li>
                <li>Anonymized analytics: retained indefinitely (contains no personal data)</li>
              </ul>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="data-security" title="7. Data Security">
              <ul className="list-disc list-inside space-y-1.5">
                <li>All connections use HTTPS/TLS encryption in transit</li>
                <li>Data is encrypted at rest via Supabase-managed infrastructure</li>
                <li>
                  Row Level Security (RLS) policies ensure users can only access their own data
                </li>
                <li>Passwords are hashed by Supabase Auth &mdash; never stored in plain text</li>
                <li>
                  Payment card details never touch our servers &mdash; processed entirely by
                  Stripe/Razorpay
                </li>
                <li>Webhook signatures are verified for all payment callbacks</li>
              </ul>
              <p>
                While we implement industry-standard security measures, no method of electronic
                transmission or storage is 100% secure. We cannot guarantee absolute security.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="your-rights" title="8. Your Rights">
              <p>You have the following rights regarding your personal data:</p>
              <ul className="list-disc list-inside space-y-1.5">
                <li>
                  <strong className="text-text-primary">Access:</strong> View your data via the
                  dashboard, people directory, and settings pages
                </li>
                <li>
                  <strong className="text-text-primary">Deletion:</strong> Request complete account
                  deletion by contacting us at the email below. All associated data (profile, people,
                  analyses, inputs, streaks, badges, purchases, referrals) will be permanently deleted
                  within 30 days
                </li>
                <li>
                  <strong className="text-text-primary">Export:</strong> Request a copy of your data
                  by contacting us
                </li>
                <li>
                  <strong className="text-text-primary">Correction:</strong> Update your display name
                  and profile information via settings
                </li>
              </ul>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-3">
                For EU Users (GDPR)
              </p>
              <p>
                You additionally have the right to object to processing, the right to data portability,
                and the right to lodge a complaint with your local data protection authority. Our lawful
                basis for processing is legitimate interest (providing the core service) and consent
                (optional features like push notifications).
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-3">
                For Indian Users (IT Act)
              </p>
              <p>
                Under Section 43A of the Information Technology Act, 2000 and the Information Technology
                (Reasonable Security Practices and Procedures and Sensitive Personal Data or Information)
                Rules, 2011, you have the right to access and correct your personal data. Mood check-in
                data and behavioral descriptions are treated as sensitive personal data under these rules.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="childrens-privacy" title="9. Children&rsquo;s Privacy">
              <p>
                ToxShield is not intended for use by children under the age of 13 (or 16 in the European
                Union). We do not knowingly collect personal data from children. If we become aware that
                we have collected data from a child, we will promptly delete it. If you believe a child
                has provided us with personal data, please contact us immediately.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="cookies" title="10. Cookies &amp; Local Storage">
              <ul className="list-disc list-inside space-y-1.5">
                <li>
                  <strong className="text-text-primary">Authentication cookies:</strong> Supabase Auth
                  uses HTTP-only session cookies for authentication. These are strictly necessary for
                  the Service to function and are exempt from consent requirements.
                </li>
                <li>
                  <strong className="text-text-primary">Analytics:</strong> Vercel Analytics uses
                  cookieless, anonymized tracking. No tracking cookies are set.
                </li>
                <li>
                  <strong className="text-text-primary">Local storage:</strong> We store a single
                  preference flag for notification prompt dismissal. No personal data is stored in
                  local storage.
                </li>
              </ul>
              <p>We do not use any third-party tracking cookies or advertising cookies.</p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="changes" title="11. Changes to This Policy">
              <p>
                We may update this Privacy Policy from time to time. Changes will be posted on this page
                with a revised &ldquo;Last updated&rdquo; date. Material changes may be communicated via
                in-app notification. Your continued use of the Service after changes constitutes acceptance
                of the updated policy.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="grievance-officer" title="12. Grievance Officer">
              <p>
                In accordance with the Information Technology Act, 2000 and rules made thereunder, the
                Grievance Officer for the purpose of this Privacy Policy is:
              </p>
              <div className="arcane-glass p-3 font-mono text-xs space-y-1">
                <p className="text-text-primary">Name: Biswa</p>
                <p>
                  Email:{' '}
                  <Link
                    href="mailto:privacy@toxshield.in"
                    className="text-neon-cyan underline underline-offset-2"
                  >
                    privacy@toxshield.in
                  </Link>
                </p>
              </div>
              <p>
                If you have any grievances regarding the processing of your personal data, you may
                contact the Grievance Officer. We will address your concerns within 30 days.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="contact" title="13. Contact Us">
              <p>
                If you have questions about this Privacy Policy or your personal data, contact us at:
              </p>
              <div className="arcane-glass p-3 font-mono text-xs space-y-1">
                <p>
                  Email:{' '}
                  <Link
                    href="mailto:privacy@toxshield.in"
                    className="text-neon-cyan underline underline-offset-2"
                  >
                    privacy@toxshield.in
                  </Link>
                </p>
                <p>
                  Website:{' '}
                  <Link
                    href="https://toxshield.in"
                    className="text-neon-cyan underline underline-offset-2"
                  >
                    toxshield.in
                  </Link>
                </p>
              </div>
            </LegalSection>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-center gap-4 pb-safe">
            <Link
              href="/terms"
              className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1"
            >
              Terms of Service
            </Link>
            <span className="text-text-secondary/20">|</span>
            <Link
              href="/"
              className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1"
            >
              Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
