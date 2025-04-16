// src/api/utils.js

import axios from 'axios';
import { API_URL } from './config';

export async function fetchCategories() {
    try {
      const response = await axios.get(`${API_URL}/categories`);
      return response.data;  // Assuming the response is an array of categories
    } catch (error) {
      console.error('Error fetching categories:', error);
      return [];
    }
  }
  
  // Fetch suppliers from API
  export async function fetchSuppliers() {
    try {
      const response = await axios.get(`${API_URL}/suppliers`);
      return response.data;  // Assuming the response is an array of suppliers
    } catch (error) {
      console.error('Error fetching suppliers:', error);
      return [];
    }
  }