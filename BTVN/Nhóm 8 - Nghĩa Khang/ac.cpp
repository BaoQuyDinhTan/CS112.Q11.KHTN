// TEST 3
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
const int MAX_CELL = MAX_N * MAX_N;
const int mod = 1e9 + 7; // 998244353
const int inf = 1e9;

int n, m, r;

struct CamBien {
    int x, y, c;
};

CamBien a[MAX_N];
bitset<MAX_CELL> cover[MAX_N];
bitset<MAX_CELL> fullMask;
double centerPenalty[MAX_N];
int coverSize[MAX_N];
vector<int> cellsCovered[MAX_N];
int totalCells;
mt19937 globalRng((uint32_t)chrono::steady_clock::now().time_since_epoch().count());

// Tùy chỉnh để bật/tắt từng module tham lam.
struct ModuleToggle {
    bool stratPureRatio = true;
    bool stratCenterFavor = true;
    bool stratCenterHeavy = true;
    bool stratRandomLight = true;
    bool stratRandomMedium = true;
    bool stratRandomInverse = true;
    bool stratRandomPool = true;
    bool presetSingles = true;
    bool presetPairs = true;
    bool presetTriples = true;
    bool presetQuads = true;
    bool localPrune = true;
    bool localDrop1 = true;
    bool localDrop2 = true;
    bool localDrop3 = true;
    bool localShake = true;
} config;

struct Heuristic {
    double beta;
    double centerWeight;
    double randomWeight;
    unsigned seed;
};

struct Result {
    bool ok = false;
    long long cost = 0;
    vector<int> picks;
};

Result runGreedy(const vector<int>& preset, const vector<bool>* forbid, const Heuristic& h);

struct GreedyModule {
    string name;
    Heuristic spec;
    bool enabled = true;

    Result solve(const vector<int>& preset, const vector<bool>* forbid) const {
        if (!enabled) return {};
        return runGreedy(preset, forbid, spec);
    }
};

struct PresetModule {
    string name;
    bool enabled = true;
    function<void(const vector<int>& forced, const vector<int>& pool, const function<void(vector<int>)>& addPreset)> builder;

    void apply(const vector<int>& forced, const vector<int>& pool, const function<void(vector<int>)>& addPreset) const {
        if (!enabled || !builder) return;
        builder(forced, pool, addPreset);
    }
};

bool betterResult(const Result& A, const Result& B) {
    if (!A.ok) return false;
    if (!B.ok) return true;
    if (A.cost != B.cost) return A.cost < B.cost;
    if (A.picks.size() != B.picks.size()) return A.picks.size() < B.picks.size();
    return A.picks < B.picks;
}

Result runGreedy(const vector<int>& preset, const vector<bool>* forbid, const Heuristic& h) {
    bitset<MAX_CELL> uncovered = fullMask;
    vector<bool> used(m + 1, false);
    vector<int> picks;
    long long totalCost = 0;
    int uncoveredCells = totalCells;

    auto applySensor = [&](int id) -> bool {
        if (id < 1 || id > m) return false;
        if (forbid && (*forbid)[id]) return false;
        if (used[id]) return true;
        used[id] = true;
        picks.pb(id);
        totalCost += a[id].c;
        int gain = (cover[id] & uncovered).count();
        if (gain) {
            uncovered &= ~cover[id];
            uncoveredCells -= gain;
        }
        return true;
    };

    for (int id : preset) {
        if (!applySensor(id)) {
            return {false, 0, {}};
        }
    }

    vector<double> randomNoise(m + 1, 0.0);
    if (h.randomWeight > 0) {
        mt19937 rng(h.seed);
        uniform_real_distribution<double> distNoise(0.0, 1.0);
        for (int i = 1; i <= m; ++i) {
            randomNoise[i] = distNoise(rng);
        }
    }

    while (uncoveredCells > 0) {
        int bestId = -1;
        double bestScore = 1e100;
        int bestGain = 0;
        int bestCost = 0;
        for (int i = 1; i <= m; ++i) {
            if (used[i]) continue;
            if (forbid && (*forbid)[i]) continue;
            bitset<MAX_CELL> contrib = cover[i] & uncovered;
            int gain = contrib.count();
            if (!gain) continue;
            double denom = (h.beta == 1.0 ? gain : pow((double)gain, h.beta));
            double score = (double)a[i].c + h.centerWeight * centerPenalty[i];
            if (denom > 0) score /= denom;
            if (h.randomWeight > 0) score += h.randomWeight * randomNoise[i];
            bool take = false;
            if (score < bestScore - 1e-12) take = true;
            else if (fabs(score - bestScore) <= 1e-12) {
                if (a[i].c < bestCost) take = true;
                else if (a[i].c == bestCost) {
                    if (gain > bestGain) take = true;
                    else if (gain == bestGain && i < bestId) take = true;
                }
            }
            if (take) {
                bestId = i;
                bestScore = score;
                bestGain = gain;
                bestCost = a[i].c;
            }
        }
        if (bestId == -1) break;
        applySensor(bestId);
    }

    if (uncoveredCells > 0) {
        return {false, 0, {}};
    }

    sort(all(picks));
    return {true, totalCost, picks};
}

class LocalOptimizer {
public:
    LocalOptimizer(const ModuleToggle& cfg,
                   const vector<int>& forced,
                   const vector<bool>& baseForced,
                   const vector<GreedyModule>& strategies)
        : cfg(cfg), forced(forced), baseForced(baseForced), strategies(strategies) {
        for (const auto& module : strategies) {
            if (module.enabled) activeStrategies.pb(&module);
        }
    }

    bool run(Result& best) const {
        if (!best.ok || activeStrategies.empty()) return false;
        for (int outer = 0; outer < 8; ++outer) {
            bool changed = false;
            if (cfg.localPrune && pruneRedundant(best)) changed = true;
            else if (cfg.localDrop1 && dropSearch(best, 1, 18, 0)) changed = true;
            else if (cfg.localDrop2 && dropSearch(best, 2, 14, 90)) changed = true;
            else if (cfg.localDrop3 && dropSearch(best, 3, 10, 60)) changed = true;
            else if (cfg.localShake && randomShake(best, 6, 3, 5)) changed = true;
            if (!changed) break;
        }
        return true;
    }

private:
    vector<int> rebuildOptional(const Result& best) const {
        vector<int> optional;
        for (int id : best.picks) {
            if (!baseForced[id]) optional.pb(id);
        }
        sort(all(optional), [&](int lhs, int rhs) {
            if (a[lhs].c != a[rhs].c) return a[lhs].c > a[rhs].c;
            if (coverSize[lhs] != coverSize[rhs]) return coverSize[lhs] > coverSize[rhs];
            return lhs > rhs;
        });
        return optional;
    }

    bool attemptWithForbidden(Result& best, const vector<int>& blockList) const {
        if (blockList.empty()) return false;
        vector<bool> forbid(m + 1, false);
        for (int id : blockList) {
            if (id < 1 || id > m || baseForced[id]) return false;
            forbid[id] = true;
        }
        bool improved = false;
        for (const auto* module : activeStrategies) {
            Result cand = module->solve(forced, &forbid);
            if (betterResult(cand, best)) {
                best = cand;
                improved = true;
            }
        }
        return improved;
    }

    bool pruneRedundant(Result& best) const {
        if (!best.ok) return false;
        vector<int> coverCnt(totalCells, 0);
        vector<bool> keep(m + 1, false);
        for (int id : best.picks) {
            keep[id] = true;
            for (int cell : cellsCovered[id]) {
                coverCnt[cell]++;
            }
        }
        bool changed = false;
        bool progress = true;
        while (progress) {
            progress = false;
            vector<int> order = rebuildOptional(best);
            for (int id : order) {
                if (!keep[id]) continue;
                bool removable = true;
                for (int cell : cellsCovered[id]) {
                    if (coverCnt[cell] <= 1) {
                        removable = false;
                        break;
                    }
                }
                if (!removable) continue;
                keep[id] = false;
                for (int cell : cellsCovered[id]) {
                    coverCnt[cell]--;
                }
                best.cost -= a[id].c;
                progress = true;
                changed = true;
            }
        }
        if (changed) {
            vector<int> filtered;
            for (int id : best.picks) {
                if (keep[id]) filtered.pb(id);
            }
            sort(all(filtered));
            best.picks.swap(filtered);
        }
        return changed;
    }

    bool dropSearch(Result& best, int dropCount, int candidateLimit, int comboLimit) const {
        vector<int> optional = rebuildOptional(best);
        if ((int)optional.size() < dropCount) return false;
        if (candidateLimit > 0 && (int)optional.size() > candidateLimit) {
            optional.resize(candidateLimit);
        }
        if (dropCount == 1) {
            for (int id : optional) {
                if (attemptWithForbidden(best, {id})) return true;
            }
        } else if (dropCount == 2) {
            int tested = 0;
            for (int i = 0; i + 1 < (int)optional.size(); ++i) {
                for (int j = i + 1; j < (int)optional.size(); ++j) {
                    if (attemptWithForbidden(best, {optional[i], optional[j]})) return true;
                    if (comboLimit > 0 && ++tested >= comboLimit) return false;
                }
            }
        } else if (dropCount == 3) {
            int tested = 0;
            for (int i = 0; i + 2 < (int)optional.size(); ++i) {
                for (int j = i + 1; j + 1 < (int)optional.size(); ++j) {
                    for (int k = j + 1; k < (int)optional.size(); ++k) {
                        if (attemptWithForbidden(best, {optional[i], optional[j], optional[k]})) return true;
                        if (comboLimit > 0 && ++tested >= comboLimit) return false;
                    }
                }
            }
        }
        return false;
    }

    bool randomShake(Result& best, int attempts, int minDrop, int maxDrop) const {
        vector<int> optional = rebuildOptional(best);
        if (optional.empty()) return false;
        uniform_int_distribution<int> distDrop(minDrop, maxDrop);
        for (int iter = 0; iter < attempts; ++iter) {
            int dropCnt = distDrop(globalRng);
            dropCnt = max(1, min(dropCnt, (int)optional.size()));
            shuffle(optional.begin(), optional.end(), globalRng);
            vector<int> block(optional.begin(), optional.begin() + dropCnt);
            if (attemptWithForbidden(best, block)) return true;
        }
        return false;
    }

    const ModuleToggle& cfg;
    const vector<int>& forced;
    const vector<bool>& baseForced;
    const vector<GreedyModule>& strategies;
    vector<const GreedyModule*> activeStrategies;
};

signed main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m >> r;
    for (int i = 1; i <= m; i++) {
        cin >> a[i].x >> a[i].y >> a[i].c;
    }

    totalCells = n * n;
    fullMask.reset();
    for (int cell = 0; cell < totalCells; ++cell) {
        fullMask.set(cell);
    }

    vector<int> cellCover(totalCells, 0);
    vector<int> cellUnique(totalCells, -1);
    for (int i = 1; i <= m; ++i) {
        cover[i].reset();
        coverSize[i] = 0;
        cellsCovered[i].clear();
        int x1 = max(1, a[i].x - r);
        int x2 = min(n, a[i].x + r);
        int y1 = max(1, a[i].y - r);
        int y2 = min(n, a[i].y + r);
        if (x1 > x2 || y1 > y2) continue;
        for (int x = x1; x <= x2; ++x) {
            for (int y = y1; y <= y2; ++y) {
                int cellId = (x - 1) * n + (y - 1);
                if (!cover[i].test(cellId)) {
                    cover[i].set(cellId);
                    coverSize[i]++;
                    cellsCovered[i].pb(cellId);
                    cellCover[cellId]++;
                    if (cellCover[cellId] == 1) cellUnique[cellId] = i;
                    else cellUnique[cellId] = -1;
                }
            }
        }
    }

    vector<int> forced;
    vector<bool> forcedMark(m + 1, false);
    for (int cell = 0; cell < totalCells; ++cell) {
        if (cellCover[cell] == 0) {
            cout << -1 << '\n';
            return 0;
        }
        if (cellCover[cell] == 1) {
            int id = cellUnique[cell];
            if (id >= 1 && !forcedMark[id]) {
                forcedMark[id] = true;
                forced.pb(id);
            }
        }
    }
    sort(all(forced));

    double center = (n + 1) / 2.0;
    for (int i = 1; i <= m; ++i) {
        centerPenalty[i] = (abs(a[i].x - center) + abs(a[i].y - center)) / max(1, n);
    }

    vector<int> sensorOrder;
    sensorOrder.reserve(m);
    for (int i = 1; i <= m; ++i) sensorOrder.pb(i);
    sort(all(sensorOrder), [&](int lhs, int rhs) {
        double gainL = max(1, coverSize[lhs]);
        double gainR = max(1, coverSize[rhs]);
        double ratioL = (double)a[lhs].c / gainL;
        double ratioR = (double)a[rhs].c / gainR;
        if (ratioL != ratioR) return ratioL < ratioR;
        if (coverSize[lhs] != coverSize[rhs]) return coverSize[lhs] > coverSize[rhs];
        return lhs < rhs;
    });

    vector<GreedyModule> strategyModules;
    auto addStrategy = [&](const string& name, const Heuristic& spec, bool enabledFlag) {
        strategyModules.push_back({name, spec, enabledFlag});
    };

    addStrategy("PureRatio", {1.0, 0.0, 0.0, 0u}, config.stratPureRatio);
    addStrategy("CenterFavor", {0.9, -0.05, 0.0, 0u}, config.stratCenterFavor);
    addStrategy("CenterHeavy", {1.2, 0.08, 0.0, 0u}, config.stratCenterHeavy);
    addStrategy("RandomLight", {1.0, 0.0, 0.02, 712387u}, config.stratRandomLight);
    addStrategy("RandomMedium", {1.4, 0.03, 0.05, 314159u}, config.stratRandomMedium);
    addStrategy("RandomInverse", {0.8, -0.02, 0.04, 926535u}, config.stratRandomInverse);

    if (config.stratRandomPool) {
        int extraHeuristics = max(4, min(10, m / 10 + 4));
        uniform_real_distribution<double> distBeta(0.75, 1.45);
        uniform_real_distribution<double> distCenter(-0.08, 0.12);
        uniform_real_distribution<double> distNoise(0.0, 0.08);
        for (int iter = 0; iter < extraHeuristics; ++iter) {
            string name = "RandomPool#" + to_string(iter + 1);
            Heuristic spec = {
                distBeta(globalRng),
                distCenter(globalRng),
                distNoise(globalRng),
                globalRng()
            };
            addStrategy(name, spec, true);
        }
    }

    bool hasActiveStrategy = false;
    for (const auto& module : strategyModules) {
        if (module.enabled) {
            hasActiveStrategy = true;
            break;
        }
    }
    if (!hasActiveStrategy) {
        addStrategy("FallbackRatio", {1.0, 0.0, 0.0, 0u}, true);
    }

    int poolSize = min((int)sensorOrder.size(), 12);
    vector<int> pool(sensorOrder.begin(), sensorOrder.begin() + poolSize);

    vector<PresetModule> presetModules;
    presetModules.push_back({
        "ForcedOnly",
        true,
        [](const vector<int>& forced, const vector<int>&, const function<void(vector<int>)>& add) {
            add(forced);
        }
    });
    presetModules.push_back({
        "SingleBoost",
        config.presetSingles,
        [](const vector<int>& forced, const vector<int>& pool, const function<void(vector<int>)>& add) {
            for (int id : pool) {
                auto preset = forced;
                preset.pb(id);
                add(preset);
            }
        }
    });
    presetModules.push_back({
        "PairBoost",
        config.presetPairs,
        [](const vector<int>& forced, const vector<int>& pool, const function<void(vector<int>)>& add) {
            for (int i = 0; i < (int)pool.size(); ++i) {
                for (int j = i + 1; j < (int)pool.size(); ++j) {
                    auto preset = forced;
                    preset.pb(pool[i]);
                    preset.pb(pool[j]);
                    add(preset);
                }
            }
        }
    });
    presetModules.push_back({
        "TripleBoost",
        config.presetTriples,
        [](const vector<int>& forced, const vector<int>& pool, const function<void(vector<int>)>& add) {
            if ((int)pool.size() > 7) return;
            for (int i = 0; i < (int)pool.size(); ++i) {
                for (int j = i + 1; j < (int)pool.size(); ++j) {
                    for (int k = j + 1; k < (int)pool.size(); ++k) {
                        auto preset = forced;
                        preset.pb(pool[i]);
                        preset.pb(pool[j]);
                        preset.pb(pool[k]);
                        add(preset);
                    }
                }
            }
        }
    });
    presetModules.push_back({
        "QuadBoost",
        config.presetQuads,
        [](const vector<int>& forced, const vector<int>& pool, const function<void(vector<int>)>& add) {
            if ((int)pool.size() > 5) return;
            for (int i = 0; i < (int)pool.size(); ++i) {
                for (int j = i + 1; j < (int)pool.size(); ++j) {
                    for (int k = j + 1; k < (int)pool.size(); ++k) {
                        for (int t = k + 1; t < (int)pool.size(); ++t) {
                            auto preset = forced;
                            preset.pb(pool[i]);
                            preset.pb(pool[j]);
                            preset.pb(pool[k]);
                            preset.pb(pool[t]);
                            add(preset);
                        }
                    }
                }
            }
        }
    });

    set<vector<int>> seenPresets;
    vector<vector<int>> presets;
    auto registerPreset = [&](vector<int> preset) {
        sort(all(preset));
        preset.erase(unique(all(preset)), preset.end());
        if (seenPresets.insert(preset).second) {
            presets.pb(move(preset));
        }
    };
    function<void(vector<int>)> addPreset = [&](vector<int> preset) {
        registerPreset(move(preset));
    };
    for (const auto& module : presetModules) {
        module.apply(forced, pool, addPreset);
    }

    Result best;
    for (const auto& preset : presets) {
        for (const auto& module : strategyModules) {
            if (!module.enabled) continue;
            Result cand = module.solve(preset, nullptr);
            if (betterResult(cand, best)) best = cand;
        }
    }

    if (!best.ok) {
        Result fallback = runGreedy(forced, nullptr, {1.0, 0.0, 0.0, 0u});
        if (fallback.ok) best = fallback;
    }

    if (best.ok) {
        vector<bool> baseForced(m + 1, false);
        for (int id : forced) {
            if (1 <= id && id <= m) baseForced[id] = true;
        }
        LocalOptimizer optimizer(config, forced, baseForced, strategyModules);
        optimizer.run(best);
    }

    if (!best.ok) {
        cout << -1 << '\n';
        return 0;
    }

    cout << best.picks.size() << '\n';
    for (int id : best.picks) {
        cout << id << ' ';
    }
    cout << '\n' << best.cost << '\n';

    return 0;
}

/*


*/
