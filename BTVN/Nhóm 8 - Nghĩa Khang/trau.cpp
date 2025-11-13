// Nhóm 4
// Bảo Quý Định Tân
// Lê Văn Thức

#include <bits/stdc++.h>

using namespace std;

template<class A, class B> bool maximize(A& x, B y) {if (x < y) return x = y, true; else return false;}
template<class A, class B> bool minimize(A& x, B y) {if (x > y) return x = y, true; else return false;}

#define     all(a)                a.begin(), a.end()
#define     pb                    push_back
#define     pf                    push_front
#define     fi                    first
#define     se                    second
// #define     int                   long long

typedef     long long             ll;
typedef     unsigned long long    ull;
typedef     double                db;
typedef     long double           ld;
typedef     pair<db, db>          pdb;
typedef     pair<ld, ld>          pld;
typedef     pair<int, int>        pii;
typedef     pair<ll, ll>          pll;
typedef     pair<ll, int>         plli;
typedef     pair<int, ll>         pill;

const int MAX_N = 100 + 5;
const int mod = 1e9 + 7; // 998244353
const int inf = 1e9;

int n, m, r;

struct CamBien {
    int x, y, c;
};

CamBien a[MAX_N];
int prefSum[MAX_N][MAX_N];

signed main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m >> r;
    for (int i = 1; i <= m; i++) {
        cin >> a[i].x >> a[i].y >> a[i].c;
    }

    int ans = inf;
    vector<int> ansList;

    for (int mask = 0; mask < (1 << m); mask++) {
        int sum = 0;
        vector<int> currList;
        for (int i = 1; i <= m; i++) {
            if (mask >> (i - 1) & 1) {
                sum += a[i].c;
                currList.pb(i);
            }
        }

        if (sum >= ans) continue;

        for (int i : currList) {
            int x = a[i].x;
            int y = a[i].y;
            prefSum[max(1, x - r)][max(1, y - r)]++;
            prefSum[max(1, x - r)][min(n + 1, y + r + 1)]--;
            prefSum[min(n + 1, x + r + 1)][max(1, y - r)]--;
            prefSum[min(n + 1, x + r + 1)][min(n + 1, y + r + 1)]++;
        }

        auto check = [&]() -> bool {
            for (int i = 1; i <= n; i++) {
                for (int j = 1; j <= n; j++) {
                    prefSum[i][j] += prefSum[i][j - 1] + prefSum[i - 1][j] - prefSum[i - 1][j - 1];
                    if (!prefSum[i][j]) return false;       
                }
            }
            return true;
        };

        if (check()) {
            ans = sum;
            ansList = currList;
        }

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                prefSum[i][j] = 0;
            }
        }
    }

    cout << ansList.size() << '\n';
    for (auto &it : ansList) {
        cout << it << ' ';
    }
    cout << '\n' << ans << '\n';

    return 0;
}

/*


*/