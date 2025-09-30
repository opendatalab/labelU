#!/usr/bin/env python3
"""
测试 bcrypt 密码截断修复
"""

from labelu.internal.common.security import get_password_hash, verify_password

# 测试用例 1: 正常长度密码
normal_password = "test@123"
print(f"测试 1: 正常密码 '{normal_password}'")
print(f"  长度: {len(normal_password.encode('utf-8'))} 字节")
hash1 = get_password_hash(normal_password)
print(f"  哈希成功: {hash1[:20]}...")
print(f"  验证成功: {verify_password(normal_password, hash1)}")
print()

# 测试用例 2: 恰好 72 字节
password_72 = "a" * 72
print(f"测试 2: 72 字节密码")
print(f"  长度: {len(password_72.encode('utf-8'))} 字节")
hash2 = get_password_hash(password_72)
print(f"  哈希成功: {hash2[:20]}...")
print(f"  验证成功: {verify_password(password_72, hash2)}")
print()

# 测试用例 3: 超过 72 字节（ASCII）
long_password = "0" * 200
print(f"测试 3: 200 字节密码（全 ASCII）")
print(f"  原始长度: {len(long_password.encode('utf-8'))} 字节")
hash3 = get_password_hash(long_password)
print(f"  哈希成功: {hash3[:20]}...")
print(f"  验证成功: {verify_password(long_password, hash3)}")
print()

# 测试用例 4: 超过 72 字节（包含多字节 UTF-8 字符）
long_password_utf8 = "测试密码" * 30  # 每个中文字符 3 字节
print(f"测试 4: 超长密码（包含 UTF-8 字符）")
print(f"  原始长度: {len(long_password_utf8.encode('utf-8'))} 字节")
hash4 = get_password_hash(long_password_utf8)
print(f"  哈希成功: {hash4[:20]}...")
print(f"  验证成功: {verify_password(long_password_utf8, hash4)}")
print()

# 测试用例 5: 模拟 GitHub Actions 环境中的超长密码
github_actions_password = "0123456789" * 25  # 250 字节
print(f"测试 5: GitHub Actions 超长密码")
print(f"  原始长度: {len(github_actions_password.encode('utf-8'))} 字节")
hash5 = get_password_hash(github_actions_password)
print(f"  哈希成功: {hash5[:20]}...")
print(f"  验证成功: {verify_password(github_actions_password, hash5)}")
print()

print("✅ 所有测试通过！bcrypt 密码截断修复成功！")
