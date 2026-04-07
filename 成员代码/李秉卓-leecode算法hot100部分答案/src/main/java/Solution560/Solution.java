package Solution560;

class Solution {
    public static void main(String[] args) {
        Solution solution = new Solution();
        int[] nums = {-1,-1,1};
        int k = 0;
        System.out.println(solution.subarraySum(nums, k)); // Output: 2
    }

    private int sum (int[] nums, int left, int right) {
        int sum = 0;
        for (int i = left; i <= right; i++) {
            sum += nums[i];
        }
        return sum;
    }

    public int subarraySum(int[] nums, int k) {
        int count = 0;
        int left = 0;
        int right = 0;
        while (right < nums.length) {
            if (left == right) {
                if (nums[left] == k) {
                    count++;
                }
                right++;
                continue;
            }
            int sum = sum(nums, left, right);
            if (sum == k) {
                count++;
                right++;
            } else if (sum < k) {
                right++;
            } else {
                left++;
            }
        }
        return count;
    }
}