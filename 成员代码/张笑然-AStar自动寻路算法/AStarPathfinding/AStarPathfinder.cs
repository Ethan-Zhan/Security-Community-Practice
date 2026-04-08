using System;
using System.Collections.Generic;
using System.Linq;

namespace AStarPathfinding
{
    public class AStarPathfinder
    {
        private GridMap map; // 地图引用，用来获取节点和邻居

        public AStarPathfinder(GridMap map)
        {
            this.map = map;
        }

        public List<Node> FindPath(Node start,Node end)
        {
            List<Node> openList = new List<Node>();        
            HashSet<Node> closedList = new HashSet<Node>(); 

            openList.Add(start); // 起点先加入开放列表

            while (openList.Count>0f)
            {
                // 从开放列表中选一个 fCost 最小的节点
                Node current = openList.OrderBy(n =>n.fCost).First();

                // 如果已经走到终点，开始回溯路径
                if (current == end)
                    return RetracePath(start, end);

                // 当前节点处理完，移到关闭列表
                openList.Remove(current);
                closedList.Add(current);

                // 遍历当前节点的所有邻居
                foreach (Node neighbor in map.GetNeighbors(current))
                {
                    // 不可走 或 已经处理过的直接跳过
                    if (!neighbor.walkable || closedList.Contains(neighbor))
                        continue;

                    // 计算从起点 -> 当前 -> 邻居 的新代价
                    int newCost = current.gCost + GetDistance(current, neighbor);

                    // 如果找到更优路径 或 邻居不在开放列表中
                    if (newCost < neighbor.gCost||!openList.Contains(neighbor))
                    {
                        neighbor.gCost = newCost;                      // 更新G值
                        neighbor.hCost = GetDistance(neighbor, end);   // 计算H值（到终点的估价）
                        neighbor.CalculateFCost();                     // 更新F = G + H
                        neighbor.parent = current;                     // 记录路径来源（用于回溯）

                        // 如果还没加入开放列表，就加进去
                        if (!openList.Contains(neighbor))
                            openList.Add(neighbor);
                    }
                }
            }

            // 如果走到这里说明没有路径
            return null;
        }

        private List<Node> RetracePath(Node start,Node end)
        {
            List<Node> path = new List<Node>();
            Node current = end;

            // 一直往父节点走，直到回到起点
            while (current != start)
            {
                path.Add(current);
                current = current.parent;
            }

            path.Add(start); // 把起点也加进去
            path.Reverse();  // 反转成 正向路径（起点 -> 终点）
            return path;
        }

        private int GetDistance(Node a,Node b)
        {
            int dx = Math.Abs(a.x-b.x);
            int dy = Math.Abs(a.y-b.y);

            // 这里是经典A*写法：优先走对角，再走直线
            if (dx > dy)
                return 14*dy+10*(dx-dy);

            return 14*dx+10*(dy-dx);
        }
    }
}