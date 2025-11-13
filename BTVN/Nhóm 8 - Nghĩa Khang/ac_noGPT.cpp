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

mt19937 rd(chrono::steady_clock::now().time_since_epoch().count());
int Rand(int l, int r) {
    return l + rd() % (r - l + 1);
}

int n, m, r;

struct CamBien {
    int x, y, c;
};

CamBien a[MAX_N];
int prefSum[MAX_N][MAX_N];
vector<pii> coverSet[MAX_N];

pair<int, vector<int>> trau() {
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

    return {ans, ansList};
}

pair<int, vector<int>> bestRatio(bool trickLord = false) {
    auto resetPref = [&]() {
        for (int i = 1; i <= n; ++i) {
            for (int j = 1; j <= n; ++j) {
                prefSum[i][j] = 0;
            }
        }
    };
    resetPref();

    int ans = 0;
    set<int> ansSet;

    set<int> unUsedList;

    for (int i = 1; i <= m; i++) {
        if (trickLord) {
            if (Rand(0, 2)) {
                unUsedList.insert(i);
            }
        }
        else {
            unUsedList.insert(i);
        }
    }

    
    int numUncover = n * n;
    while (numUncover) {
        int numCoverOfCurrBestRatio = 0;
        int bestRatioPos = -1;
        
        for (auto &i : unUsedList) {
            int numCover = 0;
            for (auto &[x, y] : coverSet[i]) {
                numCover += (!prefSum[x][y]);
            }
            if (!(~bestRatioPos) || 1ll * a[bestRatioPos].c * numCover > 1ll * a[i].c * numCoverOfCurrBestRatio) {
                numCoverOfCurrBestRatio = numCover;
                bestRatioPos = i;
            }
        }

        if (!(~bestRatioPos) || numCoverOfCurrBestRatio == 0) {
            resetPref();
            return {inf, {}};
        }
        
        for (auto &[x, y] : coverSet[bestRatioPos]) {
            prefSum[x][y]++;
        }
        numUncover -= numCoverOfCurrBestRatio;
        ans += a[bestRatioPos].c;
        ansSet.insert(bestRatioPos);
        unUsedList.erase(bestRatioPos);
    }

    int dropDelta[MAX_N][MAX_N];

    auto tryDropGroup = [&](const vector<int>& group) -> bool {
        vector<pii> touched;
        for (int id : group) {
            for (auto &[x, y] : coverSet[id]) {
                if (dropDelta[x][y] == 0) {
                    touched.pb({x, y});
                }
                dropDelta[x][y]++;
            }
        }
        bool ok = true;
        for (auto &[x, y] : touched) {
            if (prefSum[x][y] - dropDelta[x][y] <= 0) {
                ok = false;
                break;
            }
        }
        if (ok) {
            for (auto &[x, y] : touched) {
                prefSum[x][y] -= dropDelta[x][y];
            }
        }
        for (auto &[x, y] : touched) {
            dropDelta[x][y] = 0;
        }
        return ok;
    };
    
    bool improved = true;
    while (improved) {
        improved = false;
        for (auto it = ansSet.begin(); it != ansSet.end(); ) {
            int id = *it;
            if (tryDropGroup(vector<int>{id})) {
                ans -= a[id].c;
                it = ansSet.erase(it);
                improved = true;
            } else {
                ++it;
            }
        }
        if (improved) continue;
        break;
    }

    vector<int> ansList(all(ansSet));
    resetPref();
    return {ans, ansList};
}

signed main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m >> r;
    for (int i = 1; i <= m; i++) {
        cin >> a[i].x >> a[i].y >> a[i].c;
        for (int x = max(1, a[i].x - r); x <= min(n, a[i].x + r); x++) {
            for (int y = max(1, a[i].y - r); y <= min(n, a[i].y + r); y++) {
                coverSet[i].pb({x, y});
            }
        }
    }

    pair<int, vector<int>> finalAns = bestRatio();

    if (max(n, m) <= 20) {
        finalAns = trau();
    }
    else {
        for (int t = 1; t <= 333; t++) {
            auto tmp = bestRatio(true);
            if (tmp.fi < finalAns.fi) {
                finalAns = tmp;
            }
        }
    }

    // Xuat dap an
    cout << finalAns.se.size() << '\n';
    for (auto &it : finalAns.se) {
        cout << it << ' ';
    }
    cout << '\n' << finalAns.fi << '\n';

    return 0;
}

/*


*/
