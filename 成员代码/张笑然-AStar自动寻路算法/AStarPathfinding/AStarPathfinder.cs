using System;
using System.Collections.Generic;
using System.Linq;

public class AStarPathfinder
{
    private GridMap grid;

    // 移动代价常量（避免魔法数字）
    private const int STRAIGHT_COST = 10;
    private const int DIAGONAL_COST = 14;

    public AStarPathfinder(GridMap grid)
    {
        this.grid = grid;
    }

    /// <summary>
    /// 使用 A* 算法寻找最短路径
    /// 核心公式：
    /// f(n) = g(n) + h(n)
    /// g(n)：起点到当前节点的实际代价
    /// h(n)：当前节点到终点的估算代价
    /// </summary>
    public List<Node> FindPath(Node start, Node end)
    {
        List<Node> openList = new List<Node>();
        HashSet<Node> closedList = new HashSet<Node>();

        openList.Add(start);

        while (openList.Count > 0)
        {
            // TODO:
            // 当前使用 List 查找最小 fCost，时间复杂度 O(n)
            // 可优化为优先队列（最小堆）提升性能
            Node current = openList.OrderBy(n => n.fCost).First();

            openList.Remove(current);
            closedList.Add(current);

            if (current == end)
                return RetracePath(start, end);

            foreach (Node neighbor in grid.GetNeighbors(current))
            {
                if (!neighbor.walkable || closedList.Contains(neighbor))
                    continue;

                int newCost = current.gCost + GetDistance(current, neighbor);

                if (newCost < neighbor.gCost || !openList.Contains(neighbor))
                {
                    neighbor.gCost = newCost;
                    neighbor.hCost = GetDistance(neighbor, end);
                    neighbor.parent = current;

                    if (!openList.Contains(neighbor))
                        openList.Add(neighbor);
                }
            }
        }

        // 如果 openList 为空仍未找到路径，说明目标不可达
        return null;
    }

    /// <summary>
    /// 回溯路径（从终点往回找）
    /// </summary>
    private List<Node> RetracePath(Node start, Node end)
    {
        List<Node> path = new List<Node>();
        Node current = end;

        while (current != start)
        {
            path.Add(current);
            current = current.parent;
        }

        path.Reverse();
        return path;
    }

    /// <summary>
    /// 计算两个节点之间的距离（对角距离）
    /// </summary>
    private int GetDistance(Node a, Node b)
    {
        int dx = Math.Abs(a.x - b.x);
        int dy = Math.Abs(a.y - b.y);

        // 对角优先（A*常用优化）
        if (dx > dy)
            return DIAGONAL_COST * dy + STRAIGHT_COST * (dx - dy);

        return DIAGONAL_COST * dx + STRAIGHT_COST * (dy - dx);
    }
}
