# 🔒 StagDeck Security Rules

This document defines security constraints and validation rules for the StagDeck theme system.

---

## 1. Theme Variable Resolution

### 1.1 Circular Reference Prevention

**Rule:** Variable references must not form circular dependencies.

**Rationale:** Circular references would cause infinite recursion during variable resolution, leading to stack overflow or infinite loops.

**Implementation:**
- Track variables currently being resolved in a `_resolving` set
- Before resolving a variable, check if it's already in the set
- If found, raise `CircularReferenceError` with the dependency chain
- Remove variable from set after resolution completes

**Example - Invalid:**
```json
{
  "palette": {
    "color_a": "${color_b}",
    "color_b": "${color_c}",
    "color_c": "${color_a}"
  }
}
```
This creates a cycle: `color_a → color_b → color_c → color_a`

**Example - Valid:**
```json
{
  "palette": {
    "primary": "#667eea",
    "primary_light": "${primary}",
    "primary_dark": "#5a6fd6"
  }
}
```

### 1.2 Maximum Resolution Depth

**Rule:** Variable resolution depth must not exceed 10 levels.

**Rationale:** Even without circular references, deeply nested variables indicate poor theme design and can impact performance.

**Example - Invalid:**
```json
{
  "a": "${b}", "b": "${c}", "c": "${d}", "d": "${e}",
  "e": "${f}", "f": "${g}", "g": "${h}", "h": "${i}",
  "i": "${j}", "j": "${k}", "k": "#000"
}
```

---

## 2. Expression Evaluation

### 2.1 Safe Expression Evaluation

**Rule:** Only allow safe mathematical operations in computed values.

**Allowed operators:**
- Arithmetic: `+`, `-`, `*`, `/`
- Parentheses: `(`, `)`
- Numbers: integers and floats
- Variable references: `${variable_name}`

**Forbidden:**
- Function calls
- Attribute access
- Import statements
- Code execution
- String operations (except concatenation for gradients)

### 2.2 Division by Zero

**Rule:** Division operations must handle zero divisors gracefully.

**Implementation:** Return `0` or raise `ExpressionError` rather than crashing.

---

## 3. File Loading

### 3.1 Path Traversal Prevention

**Rule:** Theme file paths must not escape the themes directory.

**Implementation:** Use `resolve_safe_path()` from `stagdeck.utils.paths`

```python
from stagdeck.utils import resolve_safe_path, PathSecurityError

try:
    safe_path = resolve_safe_path(
        'themes/bright.json',
        base_dir='/app',
        allow_traversal=False,  # Prevent ../ escaping
        max_depth=3,            # Limit directory depth
    )
except PathSecurityError as e:
    # Handle security violation
    pass
```

**Forbidden patterns:**
- `../` path traversal (blocked by `allow_traversal=False`)
- Shell metacharacters: `; & | \` $ ( ) < >`
- Command substitution: `$(...)` or `${...}`
- Null bytes: `\x00`
- Absolute paths outside base directory

### 3.2 Shell Injection Prevention

**Rule:** File paths must not contain shell injection patterns.

**Implementation:** The `resolve_safe_path()` function automatically checks for:

| Pattern | Description |
|---------|-------------|
| `; & \| \`` | Shell metacharacters |
| `$( )` | Command substitution |
| `${ }` | Variable expansion |
| `> <` | I/O redirection |
| `\|\|` `&&` | Logical operators |
| `\x00` | Null bytes |

**Example - Blocked:**
```python
resolve_safe_path('themes/$(whoami).json')  # PathSecurityError
resolve_safe_path('themes/test; rm -rf /')  # PathSecurityError
```

### 3.3 Theme Inheritance Security

**Rule:** Theme references must use the symbol system or same-folder references only.

**Implementation:** The `ThemeLoader` class enforces:

1. **Symbol references** - `symbol:filename.json` where symbol is registered
2. **Same-folder references** - `filename.json` resolved relative to parent theme
3. **No path components** - Filenames cannot contain `/` or `\`
4. **JSON extension required** - All theme files must end with `.json`

**Allowed patterns:**
```python
# Symbol reference (default is built-in)
Theme.from_reference('default:bright.json')
Theme.from_reference('default:dark.json')

# Register custom symbol
SlideDeck.add_theme_path('corporate', '/path/to/corporate/themes')
Theme.from_reference('corporate:main.json')

# Same-folder reference in extends (within theme JSON)
{"extends": "bright.json"}  # Resolves relative to current theme's folder
```

**Blocked patterns:**
```python
Theme.from_reference('../etc/passwd')        # PathSecurityError
Theme.from_reference('unknown:theme.json')   # ThemeLoadError
{"extends": "/etc/passwd"}                   # PathSecurityError
{"extends": "../../secrets.json"}            # PathSecurityError
```

### 3.4 Theme Circular Inheritance Prevention

**Rule:** Theme inheritance chains must not form cycles.

**Implementation:** The loader tracks themes being loaded and raises `ThemeLoadError` if a cycle is detected.

**Example - Blocked:**
```json
// theme_a.json
{"extends": "theme_b.json"}

// theme_b.json  
{"extends": "theme_a.json"}
```
Results in: `ThemeLoadError: Circular theme inheritance detected: theme_a.json -> theme_b.json -> theme_a.json`

### 3.5 Maximum Inheritance Depth

**Rule:** Theme inheritance depth must not exceed 5 levels.

**Rationale:** Prevents performance issues and overly complex theme hierarchies.

### 3.6 File Size Limits

**Rule:** Theme JSON files must not exceed 1MB.

**Rationale:** Prevents denial of service via memory exhaustion.

---

## 4. Input Validation

### 4.1 Color Value Validation

**Rule:** Color values must be valid CSS colors.

**Allowed formats:**
- Hex: `#rgb`, `#rrggbb`, `#rrggbbaa`
- RGB: `rgb(r, g, b)`, `rgba(r, g, b, a)`
- HSL: `hsl(h, s%, l%)`, `hsla(h, s%, l%, a)`
- Named colors: `white`, `black`, `transparent`
- CSS variables: `var(--name)`

### 4.2 Numeric Value Bounds

**Rule:** Numeric values must be within reasonable bounds.

| Property | Min | Max |
|----------|-----|-----|
| `size` | 1 | 1000 |
| `opacity` | 0 | 1 |
| `border_width` | 0 | 100 |
| `radius` | 0 | 1000 |
| `spacing` | 0 | 1000 |

---

## 5. Error Handling

### 5.1 Graceful Degradation

**Rule:** Invalid theme values must fall back to defaults, not crash.

**Implementation:**
- Log warning for invalid values
- Use sensible defaults
- Continue rendering with degraded styling

### 5.2 Error Messages

**Rule:** Error messages must not expose sensitive system information.

**Forbidden in error messages:**
- Full file paths
- System usernames
- Internal implementation details
