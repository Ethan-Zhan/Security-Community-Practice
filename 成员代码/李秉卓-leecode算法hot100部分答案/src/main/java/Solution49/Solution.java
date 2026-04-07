package Solution49;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        List<List<String>> result = new ArrayList<>();
        HashMap<String, List<String>> map = new HashMap<>();
        for (String str : strs) {
            char[] chars = str.toCharArray();
            Arrays.sort(chars);
            String sortedStr = new String(chars);
            if(!map.containsKey(sortedStr)) {
                map.put(sortedStr, new ArrayList<>());
                map.get(sortedStr).add(str);
            }
            else {
                map.get(sortedStr).add(str);
            }
        }
        for (List<String> list : map.values()) {
            result.add(list);
        }

        return result;
    }
}