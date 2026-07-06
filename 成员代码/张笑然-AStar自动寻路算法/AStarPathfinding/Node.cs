using System;

namespace AStarPathfinding
{
    
    public class Node
    {
        public int x;
        public int y;
        public bool walkable;
    
        // 起点到当前节点的实际代价
        public int gCost;
    
        // 当前节点到目标节点的估算代价（启发函数）
        public int hCost;
    
        // 自动计算 fCost，避免忘记更新
        public int fCost => gCost + hCost;
    
        // 用于路径回溯
        public Node parent;
    
        public Node(int x, int y, bool walkable)
        {
            this.x = x;
            this.y = y;
            this.walkable = walkable;
        }
    
        public override string ToString()
        {
            return $"({x},{y})";
        }
    }
}
