"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/components/AuthProvider";
import PricingCard from "@/app/components/PricingCard";
import { apiFetch } from "@/app/lib/api";

interface Plan {
  id: number;
  name: string;
  display_name: string;
  price_cents: number;
  duration_days: number;
  price_display: string;
  per_month_display: string;
}

export default function PricingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/subscription/plans")
      .then((res) => res.json())
      .then((data) => setPlans(data.plans || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSubscribe = async (planId: number) => {
    if (!user) {
      router.push("/login");
      return;
    }

    try {
      const res = await apiFetch("/api/subscription/create-order", {
        method: "POST",
        body: JSON.stringify({ plan_id: planId, payment_method: "wechat" }),
      });
      const data = await res.json();
      if (data.status === "success") {
        router.push("/payment/callback?status=success");
      } else if (data.payment_url || data.qr_code_url) {
        router.push(`/payment?order_id=${data.order_id}`);
      }
    } catch {
      alert("Failed to create order");
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px" }}>
        Loading plans...
      </div>
    );
  }

  return (
    <main style={{ maxWidth: "960px", margin: "40px auto", padding: "0 24px" }}>
      <h1 style={{ textAlign: "center", fontSize: "32px", marginBottom: "8px" }}>
        Choose Your Plan
      </h1>
      <p
        style={{
          textAlign: "center",
          color: "#6b7280",
          marginBottom: "48px",
        }}
      >
        Unlock unlimited AI-powered English speaking practice
      </p>

      {/* Free tier info */}
      <div
        style={{
          textAlign: "center",
          marginBottom: "32px",
          padding: "16px",
          background: "#f9fafb",
          borderRadius: "8px",
        }}
      >
        <p style={{ fontWeight: 600, marginBottom: "4px" }}>Free Tier</p>
        <p style={{ color: "#6b7280", fontSize: "14px" }}>
          3 practices per day | Beginner level only | Basic feedback
        </p>
      </div>

      {/* Plan cards */}
      <div
        style={{
          display: "flex",
          gap: "24px",
          justifyContent: "center",
          flexWrap: "wrap",
        }}
      >
        {plans.map((plan) => (
          <PricingCard
            key={plan.id}
            name={plan.name}
            displayName={plan.display_name}
            priceDisplay={plan.price_display}
            perMonthDisplay={plan.per_month_display}
            durationDays={plan.duration_days}
            highlighted={plan.name === "quarterly"}
            onSubscribe={() => handleSubscribe(plan.id)}
          />
        ))}
      </div>

      {/* FAQ */}
      <div style={{ marginTop: "64px", maxWidth: "640px", marginInline: "auto" }}>
        <h2 style={{ textAlign: "center", marginBottom: "24px" }}>
          Frequently Asked Questions
        </h2>
        {[
          {
            q: "What do I get with a subscription?",
            a: "Unlimited daily practices, AI-generated tasks, full practice history, detailed AI feedback, and access to all difficulty levels.",
          },
          {
            q: "Can I cancel anytime?",
            a: "Subscriptions run for the purchased period and are non-recurring. You won't be charged again unless you manually renew.",
          },
          {
            q: "What payment methods are accepted?",
            a: "We currently support WeChat Pay. Alipay support is coming soon.",
          },
          {
            q: "Is there a free trial?",
            a: "All users get 3 free practices per day to try the platform before subscribing.",
          },
        ].map((faq, i) => (
          <div key={i} style={{ marginBottom: "20px" }}>
            <p style={{ fontWeight: 600, marginBottom: "4px" }}>{faq.q}</p>
            <p style={{ color: "#6b7280", fontSize: "14px" }}>{faq.a}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
