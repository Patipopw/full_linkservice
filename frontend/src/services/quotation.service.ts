import Cookies from "js-cookie";
import { QuotationCreate, QuotationResponse } from "@/types/quotation"; // Import มาใช้

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const createQuotation = async (payload: QuotationCreate): Promise<QuotationResponse> => {
  const token = Cookies.get("access_token");

  const response = await fetch(`${API_URL}/api/v1/quotations/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    const message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    throw new Error(message || "Failed to create quotation");
  }

  return data;
};

export const getQuotations = async (): Promise<QuotationResponse[]> => {
  const token = Cookies.get("access_token");
  const response = await fetch(`${API_URL}/api/v1/quotations/`, {
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch quotations");
  }

  return await response.json();
};

export const getQuotationById = async (id: string): Promise<QuotationResponse> => {
  const token = Cookies.get("access_token");
  const response = await fetch(`${API_URL}/api/v1/quotations/${id}`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch quotation details");
  return await response.json();
};