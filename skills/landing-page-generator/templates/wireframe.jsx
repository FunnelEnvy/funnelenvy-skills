import { useState } from "react";

const AnnotationTag = ({ children, color = "#E85D3A" }) => (
  <span
    style={{
      display: "inline-block",
      background: color,
      color: "#fff",
      fontSize: "9px",
      fontWeight: 700,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      padding: "2px 7px",
      borderRadius: "3px",
      marginBottom: "4px",
    }}
  >
    {children}
  </span>
);

const StrategyNote = ({ children }) => (
  <div
    style={{
      borderLeft: "2px solid #E85D3A",
      paddingLeft: "12px",
      marginTop: "8px",
      fontSize: "11px",
      lineHeight: "1.5",
      color: "#8C8575",
      fontFamily: "'IBM Plex Mono', monospace",
    }}
  >
    {children}
  </div>
);

const SectionLabel = ({ number, title }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: "10px",
      marginBottom: "16px",
    }}
  >
    <div
      style={{
        width: "28px",
        height: "28px",
        borderRadius: "50%",
        background: "#1A1A18",
        color: "#F5F0E8",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "13px",
        fontWeight: 700,
        fontFamily: "'IBM Plex Mono', monospace",
        flexShrink: 0,
      }}
    >
      {number}
    </div>
    <span
      style={{
        fontSize: "13px",
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.1em",
        color: "#1A1A18",
        fontFamily: "'IBM Plex Mono', monospace",
      }}
    >
      {title}
    </span>
  </div>
);

const WireframeBox = ({ children, dashed, height, style = {} }) => (
  <div
    style={{
      border: dashed ? "1.5px dashed #C4BEB2" : "1.5px solid #C4BEB2",
      borderRadius: "6px",
      padding: "16px",
      background: dashed ? "transparent" : "#FAF8F4",
      minHeight: height || "auto",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "#8C8575",
      fontSize: "12px",
      fontFamily: "'IBM Plex Mono', monospace",
      textAlign: "center",
      ...style,
    }}
  >
    {children}
  </div>
);

const CTAButton = ({ children, primary }) => (
  <div
    style={{
      background: primary ? "#1A1A18" : "transparent",
      color: primary ? "#F5F0E8" : "#1A1A18",
      border: primary ? "none" : "2px solid #1A1A18",
      borderRadius: "6px",
      padding: "12px 28px",
      fontSize: "13px",
      fontWeight: 700,
      fontFamily: "'IBM Plex Mono', monospace",
      textTransform: "uppercase",
      letterSpacing: "0.06em",
      textAlign: "center",
      cursor: "pointer",
    }}
  >
    {children}
  </div>
);

const LightboxModal = ({ onClose }) => (
  <div
    style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(26,26,24,0.6)",
      backdropFilter: "blur(4px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
      padding: "20px",
    }}
    onClick={onClose}
  >
    <div
      style={{
        background: "#FFFDF9",
        borderRadius: "12px",
        maxWidth: "440px",
        width: "100%",
        padding: "36px 32px",
        boxShadow: "0 24px 64px rgba(0,0,0,0.2)",
        position: "relative",
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <div
        style={{
          position: "absolute",
          top: "12px",
          left: "16px",
        }}
      >
        <AnnotationTag>Lightbox Form</AnnotationTag>
      </div>
      <div
        style={{
          position: "absolute",
          top: "14px",
          right: "16px",
          cursor: "pointer",
          fontSize: "18px",
          color: "#8C8575",
          fontWeight: 300,
        }}
        onClick={onClose}
      >
        ✕
      </div>

      <div style={{ marginTop: "20px" }}>
        <div
          style={{
            textAlign: "center",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 800,
              color: "#1A1A18",
              fontFamily: "'DM Sans', sans-serif",
              marginBottom: "6px",
            }}
          >
            Book Your Personalized Demo
          </div>
          <div
            style={{
              fontSize: "13px",
              color: "#8C8575",
              fontFamily: "'IBM Plex Mono', monospace",
            }}
          >
            15 minutes. No commitment. See it in action.
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <label
              style={{
                display: "block",
                fontSize: "11px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "#1A1A18",
                marginBottom: "6px",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              First Name
            </label>
            <div
              style={{
                border: "1.5px solid #C4BEB2",
                borderRadius: "6px",
                padding: "12px 14px",
                fontSize: "13px",
                color: "#C4BEB2",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              Jane
            </div>
          </div>
          <div>
            <label
              style={{
                display: "block",
                fontSize: "11px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "#1A1A18",
                marginBottom: "6px",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              Work Email
            </label>
            <div
              style={{
                border: "1.5px solid #C4BEB2",
                borderRadius: "6px",
                padding: "12px 14px",
                fontSize: "13px",
                color: "#C4BEB2",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              jane@company.com
            </div>
          </div>
          <StrategyNote>
            ZoomInfo enriches company, title, size, revenue, tech stack from work email. No need to ask the human.
          </StrategyNote>
          <div style={{ marginTop: "4px" }}>
            <CTAButton primary>Book My Demo →</CTAButton>
          </div>
          <StrategyNote>
            On submit → redirect to inline calendar embed (Chili Piper / Calendly). Prospect books their own slot while intent is hot.
          </StrategyNote>
        </div>
      </div>
    </div>
  </div>
);

export default function Wireframe() {
  const [showLightbox, setShowLightbox] = useState(false);
  const [activeTab, setActiveTab] = useState("desktop");

  return (
    <>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=IBM+Plex+Mono:wght@400;500;700&display=swap"
        rel="stylesheet"
      />

      {showLightbox && <LightboxModal onClose={() => setShowLightbox(false)} />}

      <div
        style={{
          minHeight: "100vh",
          background: "#EEEBE4",
          fontFamily: "'DM Sans', sans-serif",
          padding: "32px 20px",
        }}
      >
        {/* Header */}
        <div style={{ maxWidth: "780px", margin: "0 auto 32px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "12px",
            }}
          >
            <div>
              <div
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.15em",
                  color: "#E85D3A",
                  fontFamily: "'IBM Plex Mono', monospace",
                  marginBottom: "6px",
                }}
              >
                Annotated Wireframe
              </div>
              <h1
                style={{
                  fontSize: "28px",
                  fontWeight: 800,
                  color: "#1A1A18",
                  margin: 0,
                  lineHeight: 1.2,
                }}
              >
                B2B Paid Landing Page
              </h1>
              <p
                style={{
                  fontSize: "13px",
                  color: "#8C8575",
                  margin: "6px 0 0",
                  fontFamily: "'IBM Plex Mono', monospace",
                }}
              >
                Mid-ACV / Book a Demo / ZoomInfo Enrichment
              </p>
            </div>
            <div
              style={{
                display: "flex",
                gap: "0",
                border: "1.5px solid #C4BEB2",
                borderRadius: "6px",
                overflow: "hidden",
              }}
            >
              {["desktop", "mobile"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: "8px 16px",
                    fontSize: "11px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    fontFamily: "'IBM Plex Mono', monospace",
                    border: "none",
                    cursor: "pointer",
                    background:
                      activeTab === tab ? "#1A1A18" : "transparent",
                    color: activeTab === tab ? "#F5F0E8" : "#8C8575",
                  }}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <div
            style={{
              marginTop: "16px",
              padding: "12px 16px",
              background: "#1A1A18",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span style={{ fontSize: "14px" }}>👆</span>
            <span
              style={{
                fontSize: "11px",
                color: "#F5F0E8",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              Click any CTA button to preview the lightbox form experience
            </span>
          </div>
        </div>

        {/* Wireframe Page */}
        <div
          style={{
            maxWidth: activeTab === "mobile" ? "390px" : "780px",
            margin: "0 auto",
            background: "#FFFDF9",
            borderRadius: "12px",
            border: "1.5px solid #C4BEB2",
            overflow: "hidden",
            transition: "max-width 0.3s ease",
          }}
        >
          {/* Browser Chrome */}
          <div
            style={{
              background: "#F5F0E8",
              padding: "10px 16px",
              borderBottom: "1.5px solid #C4BEB2",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#E85D3A",
              }}
            />
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#D4A843",
              }}
            />
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#6B9E6B",
              }}
            />
            <div
              style={{
                flex: 1,
                background: "#EEEBE4",
                borderRadius: "4px",
                padding: "4px 12px",
                marginLeft: "8px",
                fontSize: "10px",
                color: "#8C8575",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              yourproduct.com/demo
            </div>
          </div>

          {/* Page Content */}
          <div style={{ padding: activeTab === "mobile" ? "24px 16px" : "32px 40px" }}>
            
            {/* SECTION 1: NO NAV */}
            <div style={{ marginBottom: "12px" }}>
              <AnnotationTag color="#8C8575">No Navigation</AnnotationTag>
              <StrategyNote>
                Remove all nav links. Zero escape routes. Every element on this page serves one goal: book the demo.
              </StrategyNote>
            </div>

            {/* Minimal top bar */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "40px",
                paddingBottom: "16px",
                borderBottom: "1px solid #EEEBE4",
              }}
            >
              <WireframeBox dashed style={{ width: "120px", height: "32px", padding: "4px" }}>
                Logo
              </WireframeBox>
              <div style={{ fontSize: "11px", color: "#8C8575", fontFamily: "'IBM Plex Mono', monospace" }}>
                No nav links
              </div>
            </div>

            {/* SECTION 2: HERO */}
            <div style={{ marginBottom: "48px" }}>
              <SectionLabel number="1" title="Hero Section" />
              <AnnotationTag>Above the Fold</AnnotationTag>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: activeTab === "mobile" ? "1fr" : "1.2fr 1fr",
                  gap: "32px",
                  marginTop: "16px",
                  alignItems: "center",
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: activeTab === "mobile" ? "22px" : "28px",
                      fontWeight: 800,
                      color: "#1A1A18",
                      lineHeight: 1.2,
                      marginBottom: "12px",
                    }}
                  >
                    [Outcome-Driven Headline]
                  </div>
                  <StrategyNote>
                    Mirror your ad copy exactly. If the ad says "Cut onboarding time by 60%" this headline says the same thing. Message match = trust.
                  </StrategyNote>

                  <div
                    style={{
                      fontSize: "14px",
                      color: "#8C8575",
                      lineHeight: 1.6,
                      margin: "16px 0",
                    }}
                  >
                    [Subheadline: 1 sentence explaining HOW the product delivers the outcome above]
                  </div>

                  <div
                    style={{ display: "inline-block", cursor: "pointer" }}
                    onClick={() => setShowLightbox(true)}
                  >
                    <CTAButton primary>Book Your Demo →</CTAButton>
                  </div>
                  <StrategyNote>
                    Button triggers lightbox. No form visible in hero. CTA copy should match the ad's promise.
                  </StrategyNote>
                </div>

                <WireframeBox dashed height="200px">
                  Product Screenshot / Short GIF
                  <br />
                  (show the product in action)
                </WireframeBox>
              </div>
            </div>

            {/* SECTION 3: SOCIAL PROOF BAR */}
            <div style={{ marginBottom: "48px" }}>
              <SectionLabel number="2" title="Social Proof Bar" />
              <div
                style={{
                  textAlign: "center",
                  fontSize: "11px",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  color: "#8C8575",
                  fontFamily: "'IBM Plex Mono', monospace",
                  marginBottom: "16px",
                }}
              >
                Trusted by teams at
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: activeTab === "mobile" ? "16px" : "32px",
                  flexWrap: "wrap",
                }}
              >
                {[1, 2, 3, 4, 5].map((i) => (
                  <WireframeBox key={i} dashed style={{ width: "80px", height: "36px", padding: "4px" }}>
                    Logo {i}
                  </WireframeBox>
                ))}
              </div>
              <StrategyNote>
                Use recognizable logos from your best customers. Instant credibility. This is the fastest trust signal on the page.
              </StrategyNote>
            </div>

            {/* SECTION 4: PAIN / SOLUTION */}
            <div style={{ marginBottom: "48px" }}>
              <SectionLabel number="3" title="Problem → Solution" />

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: activeTab === "mobile" ? "1fr" : "1fr 1fr 1fr",
                  gap: "16px",
                  marginBottom: "12px",
                }}
              >
                {[
                  { pain: "[Pain Point 1]", solution: "[How you solve it]" },
                  { pain: "[Pain Point 2]", solution: "[How you solve it]" },
                  { pain: "[Pain Point 3]", solution: "[How you solve it]" },
                ].map((item, i) => (
                  <div
                    key={i}
                    style={{
                      background: "#FAF8F4",
                      border: "1.5px solid #EEEBE4",
                      borderRadius: "8px",
                      padding: "20px",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "14px",
                        fontWeight: 700,
                        color: "#1A1A18",
                        marginBottom: "8px",
                      }}
                    >
                      {item.pain}
                    </div>
                    <div
                      style={{
                        fontSize: "13px",
                        color: "#8C8575",
                        lineHeight: 1.5,
                      }}
                    >
                      {item.solution}
                    </div>
                  </div>
                ))}
              </div>
              <StrategyNote>
                Speak to the buyer's world, not your feature list. Frame each as: "You're dealing with X. Here's how we eliminate it." Keep copy scannable.
              </StrategyNote>
            </div>

            {/* SECTION 5: PROOF */}
            <div style={{ marginBottom: "48px" }}>
              <SectionLabel number="4" title="Quantified Proof" />

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: activeTab === "mobile" ? "1fr" : "1fr 1fr",
                  gap: "16px",
                }}
              >
                {[1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      border: "1.5px solid #C4BEB2",
                      borderRadius: "8px",
                      padding: "24px",
                      background: "#FFFDF9",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "32px",
                        fontWeight: 800,
                        color: "#E85D3A",
                        fontFamily: "'IBM Plex Mono', monospace",
                      }}
                    >
                      {i === 1 ? "147%" : "3.2x"}
                    </div>
                    <div
                      style={{
                        fontSize: "13px",
                        fontWeight: 700,
                        color: "#1A1A18",
                        margin: "4px 0",
                      }}
                    >
                      [Specific metric improvement]
                    </div>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#8C8575",
                        fontStyle: "italic",
                        lineHeight: 1.5,
                      }}
                    >
                      "[Short quote from customer]"
                      <br />
                      - Name, Title, Company
                    </div>
                  </div>
                ))}
              </div>
              <StrategyNote>
                Lead with numbers, not generic praise. "Increased pipeline 147%" beats "Great product, love it." Include name, title, and company for credibility.
              </StrategyNote>
            </div>

            {/* MID-PAGE CTA */}
            <div
              style={{
                textAlign: "center",
                marginBottom: "48px",
                padding: "32px 20px",
                background: "#F5F0E8",
                borderRadius: "8px",
              }}
            >
              <SectionLabel number="5" title="Mid-Page CTA" />
              <div
                style={{
                  fontSize: "18px",
                  fontWeight: 700,
                  color: "#1A1A18",
                  marginBottom: "6px",
                }}
              >
                See how it works for your team
              </div>
              <div
                style={{
                  fontSize: "13px",
                  color: "#8C8575",
                  marginBottom: "16px",
                  fontFamily: "'IBM Plex Mono', monospace",
                }}
              >
                15 min. Personalized to your use case. No strings.
              </div>
              <div
                style={{ display: "inline-block", cursor: "pointer" }}
                onClick={() => setShowLightbox(true)}
              >
                <CTAButton primary>Book Your Demo →</CTAButton>
              </div>
              <StrategyNote>
                Same CTA, repeated. Visitor has now seen social proof + pain/solution + results. Many will convert here.
              </StrategyNote>
            </div>

            {/* SECTION 6: OPTIONAL VIDEO */}
            <div style={{ marginBottom: "48px" }}>
              <SectionLabel number="6" title="Product Visual (Optional)" />
              <WireframeBox dashed height="240px" style={{ position: "relative" }}>
                <div>
                  <div style={{ fontSize: "32px", marginBottom: "8px" }}>▶</div>
                  60-90s Product Demo Video
                  <br />
                  or Interactive Product Screenshot
                </div>
              </WireframeBox>
              <StrategyNote>
                Keep under 90 seconds. Show the product solving the exact problem from your headline. If you don't have a strong video, a static product screenshot with callouts works. Don't force it.
              </StrategyNote>
            </div>

            {/* SECTION 7: OBJECTION HANDLING */}
            <div style={{ marginBottom: "48px" }}>
              <SectionLabel number="7" title="Objection Handling / FAQ" />
              {["How long does implementation take?", "Do you integrate with [common tool]?", "What does pricing look like?"].map(
                (q, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "14px 0",
                      borderBottom: "1px solid #EEEBE4",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span style={{ fontSize: "14px", fontWeight: 600, color: "#1A1A18" }}>
                      {q}
                    </span>
                    <span style={{ color: "#8C8575", fontSize: "18px" }}>+</span>
                  </div>
                )
              )}
              <StrategyNote>
                Address the top 3 objections your sales team hears on discovery calls. This pre-handles friction before the demo is even booked.
              </StrategyNote>
            </div>

            {/* SECTION 8: FINAL CTA */}
            <div style={{ marginBottom: "32px" }}>
              <SectionLabel number="8" title="Final CTA Block" />
              <div
                style={{
                  background: "#1A1A18",
                  borderRadius: "10px",
                  padding: activeTab === "mobile" ? "32px 20px" : "40px",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    fontSize: "22px",
                    fontWeight: 800,
                    color: "#F5F0E8",
                    marginBottom: "8px",
                  }}
                >
                  Ready to [achieve the outcome]?
                </div>
                <div
                  style={{
                    fontSize: "13px",
                    color: "#8C8575",
                    marginBottom: "20px",
                    fontFamily: "'IBM Plex Mono', monospace",
                  }}
                >
                  Join [X] teams who already have.
                </div>
                <div
                  style={{ display: "inline-block", cursor: "pointer" }}
                  onClick={() => setShowLightbox(true)}
                >
                  <div
                    style={{
                      background: "#E85D3A",
                      color: "#fff",
                      borderRadius: "6px",
                      padding: "14px 32px",
                      fontSize: "14px",
                      fontWeight: 700,
                      fontFamily: "'IBM Plex Mono', monospace",
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                    }}
                  >
                    Book Your Demo →
                  </div>
                </div>
              </div>
              <StrategyNote>
                High contrast final block. Last chance conversion. The visitor who scrolled this far is highly engaged but hasn't committed yet. Make this impossible to miss.
              </StrategyNote>
            </div>

            {/* FOOTER */}
            <div
              style={{
                borderTop: "1.5px solid #EEEBE4",
                paddingTop: "16px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "8px",
              }}
            >
              <AnnotationTag color="#8C8575">Minimal Footer</AnnotationTag>
              <div
                style={{
                  fontSize: "11px",
                  color: "#8C8575",
                  fontFamily: "'IBM Plex Mono', monospace",
                }}
              >
                © 2026 YourCompany / Privacy Policy / Terms
              </div>
            </div>
          </div>
        </div>

        {/* Post-Submit Flow */}
        <div
          style={{
            maxWidth: "780px",
            margin: "32px auto 0",
            background: "#1A1A18",
            borderRadius: "12px",
            padding: activeTab === "mobile" ? "24px 16px" : "32px 40px",
          }}
        >
          <div
            style={{
              fontSize: "10px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              color: "#E85D3A",
              fontFamily: "'IBM Plex Mono', monospace",
              marginBottom: "6px",
            }}
          >
            Critical: Post-Submit Flow
          </div>
          <div
            style={{
              fontSize: "20px",
              fontWeight: 800,
              color: "#F5F0E8",
              marginBottom: "20px",
            }}
          >
            What happens after form submit
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: activeTab === "mobile" ? "1fr" : "1fr 1fr 1fr",
              gap: "16px",
            }}
          >
            {[
              {
                step: "01",
                title: "Form Submitted",
                desc: "ZoomInfo enriches lead data in background. CRM record created.",
              },
              {
                step: "02",
                title: "Calendar Embed",
                desc: "Immediate redirect to inline calendar. Prospect books their own slot. No SDR lag.",
              },
              {
                step: "03",
                title: "Confirmation Page",
                desc: "Booking confirmed. Link to relevant case study. 'Add to calendar' button. Pre-demo expectations set.",
              },
            ].map((item) => (
              <div
                key={item.step}
                style={{
                  border: "1px solid #333",
                  borderRadius: "8px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    fontSize: "24px",
                    fontWeight: 800,
                    color: "#E85D3A",
                    fontFamily: "'IBM Plex Mono', monospace",
                    marginBottom: "8px",
                  }}
                >
                  {item.step}
                </div>
                <div
                  style={{
                    fontSize: "14px",
                    fontWeight: 700,
                    color: "#F5F0E8",
                    marginBottom: "6px",
                  }}
                >
                  {item.title}
                </div>
                <div
                  style={{
                    fontSize: "12px",
                    color: "#8C8575",
                    lineHeight: 1.5,
                    fontFamily: "'IBM Plex Mono', monospace",
                  }}
                >
                  {item.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* A/B Test Notes */}
        <div
          style={{
            maxWidth: "780px",
            margin: "24px auto 0",
            border: "1.5px dashed #C4BEB2",
            borderRadius: "12px",
            padding: activeTab === "mobile" ? "24px 16px" : "28px 40px",
            background: "#FAF8F4",
          }}
        >
          <div
            style={{
              fontSize: "13px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "#1A1A18",
              fontFamily: "'IBM Plex Mono', monospace",
              marginBottom: "12px",
            }}
          >
            Priority A/B Tests at Launch
          </div>
          <div
            style={{
              fontSize: "13px",
              color: "#8C8575",
              lineHeight: 2,
              fontFamily: "'IBM Plex Mono', monospace",
            }}
          >
            <strong style={{ color: "#1A1A18" }}>Test 1:</strong> Lightbox form vs. embedded hero form (biggest lever)
            <br />
            <strong style={{ color: "#1A1A18" }}>Test 2:</strong> Headline A vs. Headline B (different outcome framing)
            <br />
            <strong style={{ color: "#1A1A18" }}>Test 3:</strong> With product video vs. without
            <br />
            <strong style={{ color: "#1A1A18" }}>Test 4:</strong> Social proof above fold vs. below
          </div>
        </div>
      </div>
    </>
  );
}
