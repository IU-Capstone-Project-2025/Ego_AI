
import { FC, ReactNode } from "react";
import {
  FaLinkedinIn,
  FaFacebookF,
  FaXTwitter,
} from "react-icons/fa6";
import { IconType } from 'react-icons';
import { MdEmail } from "react-icons/md";
import { cn } from "@/lib/utils";

type FooterLinkSection = {
  title: string;
  links: { name: string; href: string }[];
};

type SocialItem = {
  icon: IconType | JSX.Element;
  href: string;
  label: string;
};

type FooterProps = {
  sections?: FooterLinkSection[];
  social?: SocialItem[];
  logo?: ReactNode;
  copyright?: string;
  bottomLinks?: { name: string; href: string }[];
  ctaButton?: { label: string; href: string };
  className?: string;
};

const defaultSections: FooterLinkSection[] = [
  {
    title: "Product",
    links: [
      { name: "EGO", href: "#" },
      { name: "The Method", href: "#" },
      { name: "How to use guide", href: "#" },
      { name: "Pricing", href: "#" },
      { name: "Download", href: "#" },
      { name: "Changelog", href: "#" },
      { name: "Roadmap", href: "#" },
      { name: "Features", href: "#" },
      { name: "Alternatives", href: "#" },
      { name: "Reviews", href: "#" },
    ],
  },
  {
    title: "Community",
    links: [
      { name: "Merch", href: "#" },
      { name: "Blog", href: "#" },
      { name: "Slack", href: "#" },
      { name: "𝕏", href: "#" },
      { name: "LinkedIn", href: "#" },
      { name: "Find us on Tool Finder", href: "#" },
    ],
  },
  {
    title: "Use cases",
    links: [
      { name: "Founders & C-Level Executives", href: "#" },
      { name: "Developers", href: "#" },
      { name: "Designers", href: "#" },
      { name: "Marketers", href: "#" },
      { name: "Sales", href: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { name: "About us", href: "#" },
      { name: "Privacy Policy", href: "#" },
      { name: "Terms of Service", href: "#" },
      { name: "Security", href: "#" },
      { name: "Contact us", href: "#" },
      { name: "Site Map", href: "#" },
    ],
  },
];

const defaultSocial: SocialItem[] = [
  { icon: <FaLinkedinIn />, href: "#", label: "LinkedIn" },
  { icon: <FaXTwitter />, href: "#", label: "X" },
  { icon: <FaFacebookF />, href: "#", label: "Facebook" },
  { icon: <MdEmail />, href: "#", label: "Email" },
];

const Footer: FC<FooterProps> = ({
  sections = defaultSections,
  social = defaultSocial,
  logo = <span className="text-[28px] text-purple-600">🅰</span>,
  copyright = "EGO:AI ©2025 — Backed by Capstone.Innopolis",
  bottomLinks = [
    { name: "Privacy Policy", href: "#" },
    { name: "Terms of Service", href: "#" },
  ],
  ctaButton,
  className,
}) => {
  return (
    <footer className={cn("bg-white text-[#1a1a1a] px-6 md:px-20 pt-16 pb-8 border-t border-[#eee]", className)}>
      {/* Top Sections */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-12">
        {sections.map((section) => (
          <div key={section.title}>
            <h4 className="font-semibold mb-4">{section.title}</h4>
            <ul className="space-y-2">
              {section.links.map((link) => (
                <li key={link.name}>
                  <a href={link.href} className="hover:underline">
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Middle Section */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 border-t border-b border-[#eaeaea] py-6">
        <div className="flex items-center gap-4 text-sm">
          {logo}
          <div>{copyright}</div>
        </div>
        {ctaButton && (
          <a
            href={ctaButton.href}
            className="flex items-center gap-2 border border-purple-600 text-purple-600 rounded-2xl px-4 py-2 text-sm font-medium hover:bg-purple-50 transition"
          >
            {logo} {ctaButton.label}
          </a>
        )}
      </div>

      {/* Bottom Section */}
      <div className="flex flex-col md:flex-row justify-between items-center mt-6 text-sm">
        <div className="space-x-4 mb-2 md:mb-0">
          {bottomLinks.map((item, idx) => (
            <span key={item.name}>
              <a href={item.href} className="hover:underline">{item.name}</a>
              {idx < bottomLinks.length - 1 && <span className="mx-2">|</span>}
            </span>
          ))}
        </div>
        <div className="flex items-center space-x-4 text-purple-600 text-lg">
          {social.map((s) => (
            <a key={s.label} href={s.href} aria-label={s.label}>
              {s.icon}
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
};

export default Footer;