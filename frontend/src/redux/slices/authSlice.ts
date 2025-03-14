import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { 
  login as loginApi, 
  register as registerApi
} from '../../api/auth';
import { getCurrentUser as getCurrentUserApi } from '../../api/users';
import { 
  LoginRequest, 
  UserCreate, 
  User, 
  LoginResponse 
} from '../../types/user';

// 定义状态类型
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,
};

// 异步登录
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginRequest, { dispatch, rejectWithValue }) => {
    try {
      console.log('Redux login thunk called with credentials:', {
        username: credentials.username,
        password: '******' // 不记录实际密码
      });
      
      const response = await loginApi(credentials);
      console.log('Login API response:', response);
      
      // 保存token到localStorage
      localStorage.setItem('token', response.access_token);
      console.log('Token saved to localStorage');
      
      // 登录成功后立即获取用户信息
      try {
        console.log('Fetching user info after successful login');
        dispatch(getCurrentUser());
      } catch (userError) {
        console.error('Error fetching user info after login:', userError);
        // 即使获取用户信息失败，也不影响登录成功
      }
      
      return response;
    } catch (error: any) {
      console.error('Login thunk error:', error);
      console.error('Error response:', error.response?.data);
      return rejectWithValue(error.response?.data?.detail || '登录失败');
    }
  }
);

// 异步注册
export const register = createAsyncThunk(
  'auth/register',
  async (userData: UserCreate, { rejectWithValue }) => {
    try {
      console.log('Redux register thunk called with userData:', {
        ...userData,
        password: '******' // 不记录实际密码
      });
      
      // 确保full_name不是空字符串
      const processedUserData = {
        ...userData,
        full_name: userData.full_name?.trim() || undefined
      };
      
      console.log('Processed userData:', {
        ...processedUserData,
        password: '******' // 不记录实际密码
      });
      
      const response = await registerApi(processedUserData);
      console.log('Register API response:', response);
      
      return response;
    } catch (error: any) {
      console.error('Register thunk error:', error);
      console.error('Error response:', error.response?.data);
      return rejectWithValue(error.response?.data?.detail || '注册失败');
    }
  }
);

// 获取当前用户信息
export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getCurrentUserApi();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取用户信息失败');
    }
  }
);

// 创建切片
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // 登出
    logout: (state) => {
      localStorage.removeItem('token');
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    // 清除错误
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 登录
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<LoginResponse>) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 注册
    builder
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取当前用户信息
    builder
      .addCase(getCurrentUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCurrentUser.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        // 如果获取用户信息失败，可能是token无效，清除认证状态
        state.isAuthenticated = false;
        state.token = null;
        localStorage.removeItem('token');
      });
  },
});

// 导出actions
export const { logout, clearError } = authSlice.actions;

// 导出reducer
export default authSlice.reducer; 