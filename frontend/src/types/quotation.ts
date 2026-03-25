// 1. Interface สำหรับรายการสินค้า (ตอนสร้าง - ยังไม่มี id)
export interface QuotationItemCreate {
  item_no: number;
  product_name?: string | null;
  product_part?: string | null;
  product_description: string;
  red_note?: string | null;
  quantity: number;
  unit?: string | null;
  price: number;
  cost: number;
  discount_item?: number;
  total_item_price: number;
  remark?: string | null;
}

// 2. Interface สำหรับรายการสินค้า (ตอนดึงจาก DB - มี id)
export interface QuotationItemResponse extends QuotationItemCreate {
  id: number;
  quotation_id: number;
}

// 3. Interface สำหรับหัวใบเสนอราคา (ตอนสร้าง)
export interface QuotationCreate {
  company_name: string;
  company_address?: string | null;
  customer_name: string;
  customer_tel?: string | null;
  customer_email?: string | null;
  quotation_date: string; 
  validity_date: string;
  sale_name: string;
  sale_id: string;
  sale_email?: string | null;
  total_amount: number;
  status: string;
  project_name?: string | null;
  items: QuotationItemCreate[]; // ใช้ตัวที่ไม่มี id
}

// 4. Interface สำหรับข้อมูลทั้งหมดที่ดึงกลับมา (Response)
export interface QuotationResponse extends Omit<QuotationCreate, 'items'> {
  id: number;
  quotation_no: string;
  creator: string;
  creator_id: string;
  created_at: string;
  // ระบุให้ items ใน Response ต้องเป็นตัวที่มี id
  items: QuotationItemResponse[]; 
}
