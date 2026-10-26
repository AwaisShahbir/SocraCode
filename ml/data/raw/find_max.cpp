#include <vector>

int find_max(const std::vector<int>& numbers) {
    if (numbers.empty()) return -1;
    int max_val = numbers[0];
    for (size_t i = 1; i < numbers.size(); i++) {
        if (numbers[i] > max_val) {
            max_val = numbers[i];
        }
    }
    return max_val;
}
