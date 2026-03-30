import Link from 'next/link';
import type { Metadata } from 'next';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { LegalSection } from '@/components/ui/legal-section';

export const metadata: Metadata = {
  title: 'Terms of Service | ToxShield',
  description:
    'ToxShield Terms of Service — rules and guidelines for using our AI-powered behavioral analysis service.',
};

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen flex flex-col bg-surface-0/50 relative overflow-hidden">
      <AuroraBackground seed={444} />

      {/* Terminal header bar */}
      <div className="relative z-10 flex items-center gap-2 px-4 py-2 arcane-glass border-b border-neon-cyan/[0.08] font-mono text-xs">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-neon-magenta/60" />
          <span className="w-2 h-2 rounded-full bg-warning-amber/60" />
          <span className="w-2 h-2 rounded-full bg-neon-mint/60" />
        </div>
        <div className="flex-1 text-center text-text-secondary">
          toxshield://terms
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
              TERMS OF SERVICE
            </h1>
            <p className="font-mono text-xs text-text-secondary">
              Last updated: March 30, 2026
            </p>
          </div>

          {/* Content */}
          <div className="arcane-glass-intense p-6 sm:p-8 space-y-8">
            <LegalSection id="acceptance" title="1. Acceptance of Terms">
              <p>
                By accessing or using ToxShield (the &ldquo;Service&rdquo;), including the website at{' '}
                <Link href="https://toxshield.in" className="text-neon-cyan underline underline-offset-2">
                  toxshield.in
                </Link>{' '}
                and the ToxShield mobile application, you agree to be bound by these Terms of Service.
                If you do not agree, do not use the Service.
              </p>
              <p>
                You must be at least 13 years old (or 16 in the European Union) to use ToxShield. By
                using the Service, you represent that you meet this age requirement.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="service-description" title="2. Service Description">
              <p>
                ToxShield is an AI-powered behavioral analysis tool. You provide descriptions of
                someone&apos;s behavior, and our AI generates a threat profile including toxicity scores,
                detected traits, pattern analysis, and protection strategies.
              </p>
              <p className="arcane-glass p-3 text-xs text-warning-amber">
                <strong>Important Disclaimer:</strong> ToxShield is{' '}
                <strong>not a substitute</strong> for professional mental health counseling, therapy,
                clinical diagnosis, or legal advice. Analysis results are AI-generated assessments
                based on user-provided text and should not be treated as clinical, diagnostic, or
                factual conclusions. If you are in immediate danger, please contact emergency services.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="user-accounts" title="3. User Accounts">
              <ul className="list-disc list-inside space-y-1.5">
                <li>You are responsible for maintaining the security of your account credentials</li>
                <li>You must provide accurate information during registration</li>
                <li>One account per person &mdash; multiple accounts are not permitted</li>
                <li>
                  You are responsible for all activity that occurs under your account
                </li>
                <li>
                  Notify us immediately if you suspect unauthorized access to your account
                </li>
              </ul>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="acceptable-use" title="4. Acceptable Use">
              <p>You agree <strong className="text-neon-magenta">not</strong> to:</p>
              <ul className="list-disc list-inside space-y-1.5">
                <li>
                  Use ToxShield to harass, stalk, threaten, or harm any person
                </li>
                <li>
                  Submit deliberately false or fabricated information to manipulate analysis results
                </li>
                <li>
                  Use analysis results to defame, discriminate against, or publicly shame individuals
                </li>
                <li>
                  Reverse-engineer, decompile, or attempt to extract the AI analysis system or prompts
                </li>
                <li>
                  Use automated tools, bots, or scrapers to access the Service
                </li>
                <li>
                  Attempt to bypass usage limits, rate limits, or payment requirements
                </li>
                <li>
                  Share your account credentials with others or allow others to use your account
                </li>
                <li>
                  Use the Service for any illegal purpose or in violation of any applicable laws
                </li>
              </ul>
              <p>
                We reserve the right to suspend or terminate accounts that violate these terms without
                prior notice.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="ai-disclaimer" title="5. AI-Generated Content Disclaimer">
              <ul className="list-disc list-inside space-y-1.5">
                <li>
                  All analysis results (toxicity scores, trait detection, pattern analysis, protection
                  strategies) are <strong className="text-text-primary">AI-generated opinions</strong>,
                  not established facts
                </li>
                <li>
                  ToxShield does not guarantee the accuracy, completeness, or reliability of any
                  analysis result
                </li>
                <li>
                  You should <strong className="text-text-primary">not</strong> make significant life
                  decisions (legal, medical, relationship) based solely on ToxShield analysis
                </li>
                <li>
                  The app identifies behavioral patterns but cannot diagnose personality disorders or
                  mental health conditions
                </li>
                <li>
                  Analysis results may vary based on the detail and accuracy of the input you provide
                </li>
                <li>
                  We strongly encourage seeking professional help for serious concerns about
                  relationships or personal safety
                </li>
              </ul>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="payment-terms" title="6. Payment Terms">
              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider">
                6.1 Analysis Packs
              </p>
              <p>
                ToxShield offers one-time analysis packs: Daily Boost, Weekly Intel, and Monthly Pro.
                These are <strong className="text-text-primary">not subscriptions</strong> &mdash; there
                are no recurring charges or auto-renewals.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                6.2 Pack Expiration
              </p>
              <p>
                Each pack has a stated duration (1 day, 7 days, or 30 days). Unused analyses within a
                pack expire when the pack duration ends. Expired analyses cannot be recovered or
                transferred.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                6.3 Payment Processing
              </p>
              <p>
                Payments are processed by Stripe (international) or Razorpay (India). Your payment card
                details are handled entirely by these processors and never touch our servers. By making
                a purchase, you also agree to the payment processor&apos;s terms of service.
              </p>

              <p className="font-mono text-xs text-neon-cyan/70 uppercase tracking-wider pt-2">
                6.4 Refund Policy
              </p>
              <p>
                All sales are final. Refunds are generally not provided once a pack is activated.
                However, if you experience a technical failure where purchased analyses could not be
                delivered, you may contact us for review on a case-by-case basis.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="intellectual-property" title="7. Intellectual Property">
              <ul className="list-disc list-inside space-y-1.5">
                <li>
                  ToxShield and all associated intellectual property (design, code, AI prompts, brand
                  assets) are owned by us
                </li>
                <li>
                  User-generated content (behavioral descriptions, chat exports) remains your property
                </li>
                <li>
                  AI-generated analysis results are licensed to you for personal, non-commercial use
                </li>
                <li>
                  You may share your analysis results (via the share card feature) but may not
                  misrepresent them as professional assessments
                </li>
                <li>
                  You grant us a limited license to process your content for the purpose of providing
                  the Service
                </li>
              </ul>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="privacy" title="8. Privacy">
              <p>
                Your use of ToxShield is also governed by our{' '}
                <Link href="/privacy" className="text-neon-cyan underline underline-offset-2">
                  Privacy Policy
                </Link>
                , which describes how we collect, use, and protect your personal data. By using the
                Service, you consent to the data practices described in the Privacy Policy.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="limitation-of-liability" title="9. Limitation of Liability">
              <p>
                To the maximum extent permitted by applicable law:
              </p>
              <ul className="list-disc list-inside space-y-1.5">
                <li>
                  The Service is provided <strong className="text-text-primary">&ldquo;as is&rdquo;</strong>{' '}
                  and <strong className="text-text-primary">&ldquo;as available&rdquo;</strong> without
                  warranties of any kind, whether express or implied
                </li>
                <li>
                  We are not liable for any decisions you make based on AI-generated analysis results
                </li>
                <li>
                  We are not liable for emotional distress arising from analysis results
                </li>
                <li>
                  We are not liable for any indirect, incidental, special, consequential, or punitive
                  damages
                </li>
                <li>
                  Our total liability to you shall not exceed the amount you paid to us in the 12 months
                  preceding the claim
                </li>
              </ul>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="termination" title="10. Termination">
              <p>
                Either party may terminate your account at any time. You may stop using the Service and
                request account deletion by contacting us. We reserve the right to suspend or terminate
                accounts that violate these Terms without prior notice.
              </p>
              <p>
                Upon termination, your data will be deleted in accordance with our{' '}
                <Link href="/privacy" className="text-neon-cyan underline underline-offset-2">
                  Privacy Policy
                </Link>
                . Provisions that by their nature should survive termination (limitation of liability,
                intellectual property, governing law) will remain in effect.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="governing-law" title="11. Governing Law">
              <p>
                These Terms shall be governed by and construed in accordance with the laws of India.
                Any disputes arising from or relating to these Terms or the Service shall be subject to
                the exclusive jurisdiction of the courts in Bangalore, India.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="changes" title="12. Changes to These Terms">
              <p>
                We may update these Terms from time to time. Changes will be posted on this page with a
                revised &ldquo;Last updated&rdquo; date. Your continued use of the Service after changes
                constitutes acceptance of the updated Terms. If we make material changes, we will notify
                you via the Service.
              </p>
            </LegalSection>

            <div className="border-t border-neon-cyan/[0.08]" />

            <LegalSection id="contact" title="13. Contact Us">
              <p>
                If you have questions about these Terms of Service, contact us at:
              </p>
              <div className="arcane-glass p-3 font-mono text-xs space-y-1">
                <p>
                  Email:{' '}
                  <Link
                    href="mailto:support@toxshield.in"
                    className="text-neon-cyan underline underline-offset-2"
                  >
                    support@toxshield.in
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
          <div className="flex items-center justify-center gap-4 pb-6">
            <Link
              href="/privacy"
              className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1"
            >
              Privacy Policy
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
