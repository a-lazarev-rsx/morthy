import { clsx, type ClassValue } from "clsx" // Imported ClassValue
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) { // Typed inputs
  return twMerge(clsx(inputs))
}
